import argparse
import asyncio
import subprocess
import sys
import threading
import webbrowser

from agentic_research.app.observability import setup_tracing
from agentic_research.app.qa import answer
from agentic_research.app.rag import index_documents, reset_index
from agentic_research.app.runner import resume_review, start_research


def serve(port: int, open_browser: bool) -> None:
    """Arranca el worker y la API juntos, y abre la interfaz en el navegador"""
    import uvicorn

    worker = subprocess.Popen([sys.executable, "-m", "agentic_research.app.worker"])
    url = f"http://localhost:{port}"
    if open_browser:
        threading.Timer(1.5, webbrowser.open, args=(url,)).start()
    print(f"Interfaz en {url} (Ctrl+C para parar)")
    try:
        uvicorn.run("agentic_research.app.api:app", port=port, log_level="warning")
    finally:
        worker.terminate()
        worker.wait(timeout=10)


def main() -> None:
    setup_tracing()
    parser = argparse.ArgumentParser(description="Asistente de investigacion")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("index", help="Indexa los documentos de data/")
    sub.add_parser("reset", help="Borra el indice")

    ask = sub.add_parser("ask", help="Hace una pregunta a los documentos")
    ask.add_argument("question")

    research = sub.add_parser("research", help="Investiga un tema con el equipo de agentes")
    research.add_argument("topic")
    research.add_argument("--detail", choices=["low", "high"], default="low")

    srv = sub.add_parser("serve", help="Arranca la interfaz web (API + worker)")
    srv.add_argument("--port", type=int, default=8000)
    srv.add_argument("--no-browser", action="store_true", help="No abrir el navegador")

    review = sub.add_parser("review", help="Aprueba o pide cambios a un borrador")
    review.add_argument("thread_id")
    group = review.add_mutually_exclusive_group(required = True)
    group.add_argument("--approve", action="store_true")
    group.add_argument("--changes", metavar="COMENTARIO")


    args = parser.parse_args()


    if args.command == "index":
        print(f"Se indexaron {index_documents()} fragmentos.")
    elif args.command == "reset":
        reset_index()
        print("Índice borrado.")
    elif args.command == "ask":
        print(answer(args.question))
    elif args.command == "research":
        asyncio.run(start_research(args.topic, args.detail))
    elif args.command == "serve":
        serve(args.port, not args.no_browser)
    elif args.command == "review":
        if args.approve:
            asyncio.run(resume_review(args.thread_id, "approve"))
        else:
            asyncio.run(resume_review(args.thread_id, "changes", args.changes))


if __name__ == "__main__":
    main()

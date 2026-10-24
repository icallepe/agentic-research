import argparse

from mi_orquestador.app.graph import build_graph
from mi_orquestador.app.models import ResearchRequest
from mi_orquestador.app.qa import answer
from mi_orquestador.app.rag import index_documents, reset_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Asistente de investigacion")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("index", help="Indexa los documentos de data/")
    sub.add_parser("reset", help="Borra el indice")

    ask = sub.add_parser("ask", help="Hace una pregunta a los documentos")
    ask.add_argument("question")

    research = sub.add_parser("research", help="Investiga un tema con el equipo de agentes")
    research.add_argument("topic")
    research.add_argument("--detail", choices=["low", "high"], default="low")

    args = parser.parse_args()

    if args.command == "index":
        print(f"Se indexaron {index_documents()} fragmentos.")
    elif args.command == "reset":
        reset_index()
        print("Indice borrado")
    elif args.command == "ask":
        print(answer(args.question))
    elif args.command == "research":
        request = ResearchRequest(topic=args.topic, detail_level=args.detail)
        result = build_graph().invoke(
            {
                "topic": request.topic,
                "sections": request.sections,
                "detail_level": request.detail_level,
            }
        )
        for step in result.get("delegation_trace", []):
            print(f"[{step['step']}] {step['route']}: {step['reason']}")
        print()
        print(result.get("draft", "(sin borrador)"))


if __name__ == "__main__":
    main()

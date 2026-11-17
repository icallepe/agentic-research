"""Genera demo/data/reports.json con informes REALES del agente, para la demo estatica.

Uso:
    uv run python -m scripts.export_demo --dry   # solo muestra el plan, NO llama a OpenAI
    uv run python -m scripts.export_demo         # genera los 4 informes (gasta OpenAI)

No modifica app/. Usa el grafo con memoria en el proceso: no necesita Redis ni API.
"""
import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agentic_research.app.config import QUEJAS_CSV
from agentic_research.app.graph import build_graph, initial_state
from agentic_research.app.stats import cargar_quejas, contar_por_tema

SALIDA = Path("demo/data/reports.json")
SECCIONES = ["causas principales", "evidencia", "recomendaciones"]

INFORMES = [
    {
        "id": "causas-principales",
        "titulo": "Causas principales de las quejas",
        "tema": "Causas principales de las quejas en transferencias de dinero",
    },
    {
        "id": "comisiones-cobros",
        "titulo": "Comisiones y cobros",
        "tema": "Comisiones, cargos y cobros que los clientes consideran injustos o inesperados",
    },
    {
        "id": "dinero-no-llego",
        "titulo": "Dinero que no llegó",
        "tema": "Dinero enviado que nunca llegó o llegó tarde al destinatario",
    },
    {
        "id": "fraude",
        "titulo": "Fraude y estafas",
        "tema": "Fraude y estafas: transferencias que los clientes dicen haber hecho engañados",
    },
]

CITA = re.compile(r"queja\s+(\d+)", re.IGNORECASE)


def ids_citados(borrador: str) -> list[str]:
    """IDs de queja que aparecen dentro de corchetes del borrador, sin repetir y en orden."""
    vistos: list[str] = []
    for corchete in re.findall(r"\[([^\]]+)\]", borrador):
        for i in CITA.findall(corchete):
            if i not in vistos:
                vistos.append(i)
    return vistos


def generar_informe(info: dict) -> dict:
    """Ejecuta el agente real hasta la revision humana y la aprueba."""
    grafo = build_graph(InMemorySaver())
    config = {"configurable": {"thread_id": info["id"]}}
    estado = initial_state(info["tema"], SECCIONES, "high")
    grafo.invoke(estado, config)
    snap = grafo.get_state(config)
    if not snap.next:
        raise RuntimeError(f"El agente no produjo borrador para '{info['id']}'")
    payload = snap.tasks[0].interrupts[0].value
    traza = snap.values.get("delegation_trace", [])
    grafo.invoke(Command(resume={"action": "approve", "feedback": ""}), config)
    return {"borrador": payload["draft"], "consultadas": payload["references"], "traza": traza}


def leer_evaluacion(ruta: Path = Path("docs/eval_question.md")) -> list[dict]:
    """Lee la tabla de docs/eval_question.md (la genera scripts/eval_truth.py)."""
    if not ruta.exists():
        return []
    filas = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) >= 3 and celdas[0].isdigit():
            filas.append({
                "n": int(celdas[0]),
                "pregunta": celdas[1],
                "correcta": celdas[2],
                "resultado": celdas[3] if len(celdas) > 3 else "",
            })
    return filas


def leer_muestra() -> list[dict]:
    """Las quejas de data/quejas.csv, para los graficos y el buscador de la demo."""
    with open(QUEJAS_CSV, newline="", encoding="utf-8") as f:
        return [
            {
                "id": fila["complaint_id"],
                "empresa": fila["company"],
                "tema": fila["issue"],
                "fecha": fila["date_received"][:10],
                "estado": fila["state"],
                "texto": fila["complaint_what_happened"],
            }
            for fila in csv.DictReader(f)
        ]


def escribir(salida: dict) -> None:
    texto = json.dumps(salida, ensure_ascii=False, indent=2)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(texto, encoding="utf-8")
    # Copia como .js: los navegadores no dejan hacer fetch de un JSON al abrir la pagina con doble clic
    SALIDA.with_suffix(".js").write_text(f"window.DEMO_DATA = {texto};\n", encoding="utf-8")


def solo_datos() -> None:
    """Actualiza la muestra y la evaluacion SIN llamar a OpenAI; conserva los informes ya generados."""
    if not SALIDA.exists():
        raise SystemExit(f"No existe {SALIDA}: genera primero los informes (sin --solo-datos).")
    salida = json.loads(SALIDA.read_text(encoding="utf-8"))
    salida["muestra"] = leer_muestra()
    salida["total_quejas"] = len(salida["muestra"])
    salida["evaluacion"] = leer_evaluacion()
    escribir(salida)
    print(f"Actualizado: {len(salida['muestra'])} quejas y evaluacion en {SALIDA} (0 llamadas a OpenAI)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Solo muestra el plan; no llama a OpenAI")
    parser.add_argument("--solo-datos", action="store_true",
                        help="Actualiza muestra y evaluacion sin llamar a OpenAI (conserva los informes)")
    args = parser.parse_args()

    if args.solo_datos:
        return solo_datos()

    if args.dry:
        print(f"Se generarian {len(INFORMES)} informes con el agente real (gasta OpenAI):")
        for i in INFORMES:
            print(f"  - {i['id']}: {i['tema']}")
        print(f"Datos de entrada: {QUEJAS_CSV}  |  Salida: {SALIDA}")
        return

    with open(QUEJAS_CSV, newline="", encoding="utf-8") as f:
        por_id = {fila["complaint_id"]: fila for fila in csv.DictReader(f)}
    conteos = contar_por_tema(cargar_quejas(), top=8)

    informes = []
    for info in INFORMES:
        print(f"Generando: {info['titulo']} ...", flush=True)
        r = generar_informe(info)
        citadas, inventadas = [], []
        for qid in ids_citados(r["borrador"]):
            fila = por_id.get(qid)
            if fila is None:
                inventadas.append(qid)  # el agente cito un ID que no existe en el CSV
                continue
            citadas.append({
                "id": qid,
                "empresa": fila["company"],
                "tema": fila["issue"],
                "fecha": fila["date_received"][:10],
                "estado": fila["state"],
                "texto": fila["complaint_what_happened"],
            })
        if inventadas:
            print(f"  AVISO: IDs citados que NO existen en el CSV: {inventadas}", file=sys.stderr)
        informes.append({
            "id": info["id"],
            "titulo": info["titulo"],
            "tema": info["tema"],
            "borrador": r["borrador"],
            "quejas_citadas": citadas,
            "ids_inexistentes": inventadas,
            "quejas_consultadas": len(r["consultadas"]),
            "pasos_supervisor": [
                {"paso": t["step"], "ruta": t["route"], "motivo": t["reason"]} for t in r["traza"]
            ],
            "conteos": conteos,
        })

    salida = {
        "generado": date.today().isoformat(),
        "total_quejas": conteos["total_quejas"],
        "fuente": "BEE-spoke-data/consumer-finance-complaints (copia publica de datos de la CFPB)",
        "evaluacion": leer_evaluacion(),
        "muestra": leer_muestra(),
        "informes": informes,
    }
    escribir(salida)
    print(f"Listo: {len(informes)} informes en {SALIDA} (y {SALIDA.with_suffix('.js')})")


if __name__ == "__main__":
    main()

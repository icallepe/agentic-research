"""Conteos exactos sobre las quejas (sin LLM, sin costo)"""
import csv
from collections import Counter

from agentic_research.app.config import QUEJAS_CSV


def cargar_quejas() -> list[dict]:
    with open(QUEJAS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def contar_por_tema(quejas: list[dict], empresa: str = "", desde: str = "", top: int = 5) -> dict:
    """Cuenta quejas por tema (campo 'issue').
    empresa: texto que debe contener el nombre de la empresa(vacio = todas)
    desde: fecha minima AAAA-MM-DD (vacio = todas)"""

    filtradas = [
        q for q in quejas
        if empresa.lower() in q["company"].lower()
        and (not desde or q["date_received"][:10] >= desde)
    ]

    conteo = Counter(q["issue"] for q in filtradas)
    total = len(filtradas)
    return {
        "total_quejas": total,
        "temas": [
            {"tema": tema, "quejas": n, "porcentaje": round(100 * n / total, 1)}
            for tema, n in conteo.most_common(top)
        ],
    }
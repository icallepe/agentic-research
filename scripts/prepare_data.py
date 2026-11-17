"""Descarga una muestra de quejas reales de la CFPB (con texto) y la guarda en data/quejas.csv.

La CFPB ya no publica las narrativas en su API ni en su fichero masivo, asi que se usa
el dataset publico BEE-spoke-data/consumer-finance-complaints de Hugging Face, que es una
copia anterior con el texto (quejas hasta febrero de 2024; los datos personales ya vienen
anonimizados como XXXX). Se consulta por la API de filas, sin descargar el dataset entero.
"""
import csv
import time
from pathlib import Path

import requests

URL = "https://datasets-server.huggingface.co/filter"
DATASET = "BEE-spoke-data/consumer-finance-complaints"
CONFIG = "has-text"  # solo quejas con narrativa
PRODUCTO = "Money transfer, virtual currency, or money service"
MUESTRA = 200
TROZOS = 8  # se toman 8 bloques repartidos por todo el dataset, para tener variedad
SALIDA = Path("data/quejas.csv")
CAMPOS = ["complaint_id", "date_received", "company", "product", "issue", "state", "complaint_what_happened"]

COLUMNAS = {
    "Complaint ID": "complaint_id",
    "Date received": "date_received",
    "Company": "company",
    "Product": "product",
    "Issue": "issue",
    "State": "state",
    "Consumer complaint narrative": "complaint_what_happened",
}


def pedir(offset: int, length: int) -> dict:
    params = {
        "dataset": DATASET,
        "config": CONFIG,
        "split": "train",
        "where": f"\"Product\"='{PRODUCTO}'",
        "offset": offset,
        "length": length,
    }
    for intento in range(5):
        r = requests.get(URL, params=params, timeout=120)
        if r.status_code < 500:
            break
        time.sleep(2 * (intento + 1))  # el servidor falla de vez en cuando: reintentar
    r.raise_for_status()
    return r.json()


def descargar() -> list[dict]:
    total = pedir(0, 1)["num_rows_total"]
    por_trozo = MUESTRA // TROZOS
    paso = max(total // TROZOS, 1)
    quejas, vistos = [], set()
    for i in range(TROZOS):
        offset = min(i * paso, max(total - por_trozo, 0))
        for item in pedir(offset, por_trozo)["rows"]:
            fila = item["row"]
            texto = (fila.get("Consumer complaint narrative") or "").strip()
            if not texto or texto == "None" or fila["Complaint ID"] in vistos:
                continue
            vistos.add(fila["Complaint ID"])
            quejas.append({nuevo: fila[orig] for orig, nuevo in COLUMNAS.items()})
    return quejas


def guardar(quejas: list[dict]) -> None:
    SALIDA.parent.mkdir(exist_ok=True)
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(quejas)


if __name__ == "__main__":
    quejas = descargar()
    if not quejas:
        raise SystemExit("No se obtuvieron quejas con texto. Revisa DATASET y PRODUCTO.")
    guardar(quejas)
    print(f"Guardadas {len(quejas)} quejas en {SALIDA}")

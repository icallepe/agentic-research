import math

from langchain_openai import OpenAIEmbeddings

from agentic_research.app.config import EMBEDDING_MODEL, check_config

check_config()
emb = OpenAIEmbeddings(model=EMBEDDING_MODEL)


def similitud(a: list[float], b: list[float]) -> float:
    """Similitud coseno: 1 = idéntico en significado, 0 = sin relación."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


frases = [
    "El codigo de verificación nunca me llego al celular",
    "No recibi el sms para confirmar mi numero",
    "Me encanta el diseño de la pantalla de inicio",
]

vectores = emb.embed_documents(frases)
print("Un vector tiene", len(vectores[0]), "numeros")

print("1 vs 2 (mismo tema, distintas palabras):",
      round(similitud(vectores[0], vectores[1]), 2))

print("1 vs 3 (temas distintos):               ",
      round(similitud(vectores[0], vectores[2]), 2))

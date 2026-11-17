import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Redis para los checkpoints de LangGraph (local con Docker o Redis Cloud).
# Si no esta definida se usa memoria (se pierde al cerrar el proceso).
REDIS_URL = os.getenv("REDIS_URL")
MODEL_NAME = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
QUEJAS_CSV = "data/quejas.csv"
MAX_CHARS_QUEJA = 1500
K_BUSQUEDA = 5
# Phoenix (observabilidad). Vacio = sin trazas.
PHOENIX_ENDPOINT = os.getenv("PHOENIX_ENDPOINT", "")


def check_config() -> None:
    if not OPENAI_API_KEY:
        raise RuntimeError("Falta OPENAI_API_KEY en el archivo .env")

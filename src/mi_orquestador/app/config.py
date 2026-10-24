import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"


def check_config() -> None:
    if not OPENAI_API_KEY:
        raise RuntimeError("Falta OPENAI_API_KEY en el archivo .env")

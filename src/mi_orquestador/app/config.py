import os

from dotenv impor load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o_mini"
EMBEDDING_MODEL = "text_embedding-3-small"


def check_comfig() -> None:
        if not OPENAI_API_KEY:
            raise RuntimeError("Falta OPENAI_API_KEY en el archivo .env")

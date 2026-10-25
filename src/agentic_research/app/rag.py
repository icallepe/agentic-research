import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agentic_research.app.config import EMBEDDING_MODEL, check_config
from agentic_research.app.models import Source

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = str(BASE_DIR / "chroma")
COLLECTION = "research"


def _vector_store() -> Chroma:
    check_config()
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        persist_directory=CHROMA_DIR,
    )


def load_chunks() -> tuple[list[Document], list[str]]:
    """Lee data/*.md y devuelve los fragmentos con sus ids estables."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=60)
    docs: list[Document] = []
    ids: list[str] = []
    for ruta in sorted(DATA_DIR.glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        for i, trozo in enumerate(splitter.split_text(texto)):
            docs.append(Document(page_content=trozo, metadata={"source": ruta.name, "chunk": i}))
            ids.append(f"{ruta.name}::{i}")
    return docs, ids


def index_documents() -> int:
    """Indexa todo. Se puede ejecutar varias veces sin duplicar."""
    docs, ids = load_chunks()
    _vector_store().add_documents(docs, ids=ids)
    return len(docs)


def reset_index() -> None:
    """Borra el indice por completo (util si eliminas o cambias muchos documentos)."""
    shutil.rmtree(CHROMA_DIR, ignore_errors=True)


def search(query: str, k: int = 4) -> list[Source]:
    resultados = _vector_store().similarity_search_with_score(query, k=k)
    return [
        Source(file=doc.metadata["source"], excerpt=doc.page_content, score=float(score))
        for doc, score in resultados
    ]

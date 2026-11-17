import csv
import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from agentic_research.app.config import EMBEDDING_MODEL, MAX_CHARS_QUEJA, QUEJAS_CSV, check_config
from agentic_research.app.models import Source

CHROMA_DIR = "chroma"
COLLECTION = "quejas"

def _vector_store() -> Chroma:
    check_config()
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        persist_directory=CHROMA_DIR,
    )


def load_chunks() -> tuple[list[Document], list[str]]:
    """Lee data/quejas.csv: una queja = un fragmento, con id estable."""
    docs: list[Document] = []
    ids: list[str] = []
    with open(QUEJAS_CSV, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            texto = fila["complaint_what_happened"].strip()[:MAX_CHARS_QUEJA]
            if not texto:
                continue
            docs.append(
                Document(
                    page_content=texto,
                    metadata={
                        "source": f"queja {fila['complaint_id']}",
                        "company": fila["company"],
                        "product": fila["product"],
                        "issue": fila["issue"],
                        "date": fila["date_received"],
                    }
                )
            )
            ids.append(f"queja::{fila['complaint_id']}")
    return docs, ids

def index_documents() -> int:
    """Indexa todo. Se puede ejecutar varias veces sin duplicar."""
    docs, ids = load_chunks()
    _vector_store().add_documents(docs, ids=ids)
    return len(docs)


def reset_index() -> None:
    """Borra el indice por completo (util si eliminas o cambias muchos documentos)."""
    shutil.rmtree(CHROMA_DIR, ignore_errors=True)


def search(query: str, k: int = 5) -> list[Source]:
    resultados = _vector_store().similarity_search_with_score(query, k=k)
    fuentes = []
    for doc, score in resultados:
        fuentes.append(
            Source(
                file=doc.metadata["source"],
                excerpt=doc.page_content,
                score=float(score),
                company=doc.metadata.get("company"),
                issue=doc.metadata.get("issue"),
                date=doc.metadata.get("date"),
            )
        )
    return fuentes
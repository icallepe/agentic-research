from agentic_research.app.core.ports import Retriever
from agentic_research.app.models import Source
from agentic_research.app.rag import search


class ChromaRetriever(Retriever):
    def search(self, query: str, k: int = 4) -> list[Source]:
        return search(query, k)
        
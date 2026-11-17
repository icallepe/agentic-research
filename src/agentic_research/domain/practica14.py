from agentic_research.app.rag import _vector_store, index_documents

print("Fragmentos indexados:", index_documents())
print("Fragmentos indexados (otra vez):", index_documents())
print("total en Chroma:", _vector_store()._collection.count())

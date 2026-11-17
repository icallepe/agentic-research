from agentic_research.app.rag import _vector_store, index_documents, reset_index

reset_index()
print("Quejas indexadas:", index_documents())
print("Total en Chroma:", _vector_store()._collection.count())

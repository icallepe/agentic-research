from mi_orquestador.app.rag import _vector_store, index_documents

print("Fragmentos indexados:", index_documents())
print("Fragmentos indexados (otra vez):", index_docuemnts())
print("total en Chroma:", _vector_store()._collection.count())

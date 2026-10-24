from mi_orquestador.app.llm import get_llm

llm = get_llm()
respuesta = llm.invoke("Explica en una frase que es una entrevista de un usuario")

print(respuesta.content)
print(respuesta.usage_metadata)


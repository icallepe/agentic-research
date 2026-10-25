from langchain_core.prompts import ChatPromptTemplate

from agentic_research.app.llm import get_llm, usage_summary

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un investigador UX senior. Responde en español",
            "de forma breve y sin inventar datos.",
        ),

        (
            "human", "define eeste termino para alguien sin experiencia: {termino}"
        ),
    ]
)

chain = prompt | get_llm()

respuesta = chain.invoke({"termino": "tasa de abandono"})
print(respuesta.content)
print(usage_summary(respuesta))

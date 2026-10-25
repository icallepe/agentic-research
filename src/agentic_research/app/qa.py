from langchain_core.prompts import ChatPromptTemplate

from agentic_research.app.llm import get_llm
from agentic_research.app.rag import search

SYSTEM = """Eres un analista de investigacion. Responde SOLO con la informacion de los fragmentos entregados.
Reglas:
1. Despues de cada afirmación, cita la fuente entre corchetes, por ejemplo [analitica]
2. Si los fragmentos no contienen la respuesta, responde exactamente:
"No hay información suficiente en los documentos"
3. Si dos fuentes se contradicen, presenta ambas versiones con su fuente y di explicitamente que hay una contradiccion. No elijas una en silencio
4. No uses conocimiento externo, ni inventes cifras"""

HUMAN = """Fragmentos:
{contexto}

Pregunta: {question}"""

_prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)])


def format_context(sources) -> str:
    return "\n\n".join(f"[{s.file}]\n{s.excerpt}" for s in sources)


def answer(question: str, k: int = 4) -> str:
    sources = search(question, k=k)
    chain = _prompt | get_llm(temperature=0)
    respuesta = chain.invoke({"contexto": format_context(sources), "question": question})
    return respuesta.content

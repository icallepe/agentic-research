
from langchain_core.prompts import ChatPromptTemplate

from agentic_research.app.llm import get_llm
from agentic_research.app.models import RouteDecision

llm = get_llm()
estructurado = llm.with_structured.output(RouteDecision)

prompt = ChatPromptTemplate.from_message(
    [
        (
            "system", "Eres un manager. Decides quien trabaja despues"),
        ("human", "Situación: {situacion}\nElige el siguiente paso."),
    ]
)

decision = (prompt | estructurado).invoke(
    {"situacion": "Aun no se a buscado ninguna información."}
)

print(type(decision))
print(decision.next)
print(decision.reason)
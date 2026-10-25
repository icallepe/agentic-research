from langchain_core.prompts import ChatPromptTemplate

from agentic_research.app.llm import get_llm
from agentic_research.app.models import RouteDecision

SYSTEM = """Eres el manager de un equipo de investigación con tres especialistas:
-researcher: busca informacion en los documentos
-analyst: mide y compara la evidencia encontrada (necesita que haya investigación)
-synthesizer: redacta el informe final (necesita investigacion; el analisis ayuda)

Reglas:
-si no hay investigacion, el siguiente paso es researcher
-si no hay investigacion pero no analisis, el siguiente paso es analyst
-si hay investigacion y analisi pero no hay borrador, el siguiente paso es synthesizer
-si hay un borrador listo, responde finish.
Responde solo con el siguiente paso y una razon de una frase."""

HUMAN = """Estado actual:
-Tema: {topic}
-Investigacion hecha: {has_research}
-analisis hecho: {has_analysis}
-Borrador listo: {has_draft}
-Pasos usados: {step_count}"""

_prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)])

def decide_route(
    topic: str,
    has_research: bool,
    has_analysis: bool,
    has_draft: bool,
    step_count: int,
) -> RouteDecision:
    llm = get_llm(temperature=0).with_structured_output(RouteDecision)
    return (_prompt | llm).invoke(
        {
            "topic": topic,
            "has_research": "si" if has_research else "no",
            "has_analysis": "si" if has_analysis else "no",
            "has_draft": "si" if has_draft else "no",
            "step_count": step_count,
        }
    )
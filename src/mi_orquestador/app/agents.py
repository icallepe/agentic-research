from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from mi_orquestador.app.llm import get_llm
from mi_orquestador.app.qa import format_context
from mi_orquestador.app.rag import search
from mi_orquestador.app.state import ResearchState, current

import re
from collections import Counter



RESEARCHER_SYSTEM = """Eres un investigador. Tu trabajo es reunir evidencia en los documentos usando la herramienta search_documents.
Reglas:
-Haz entre 2 y 3 busquedas con consultas distintas y especificas.
-Cuando tengas suficiente evidencia, responde con un resumen de hallazgos.
-Cita la fuente de cada dato entre corchetes, por ejemplo [analitica.md]
-Si encuentras datos que se contradicen entre fuentes, señalalo explicitamente
-Si no encuentras informacion relevante, dilo. No inventes datos
"""



SYNTH_SYSTEM = """Eres un redactor de informes de investigación. Escribes SOLO con la información de las contribuciones recibidas.
Reglas:
-Estructura el informe con estas secciones, en este orden: {sections}.
-Añade al final una sección "Incertidumbres" donde indiques datos que se contradicen o que faltan.
-Cita la fuente de cada afirmación entre corchetes, por ejemplo [entrevistas.md]
-Nunca inventes cifras ni fuentes.
-Nivel de detalle: {detail}."""

SYNTH_HUMAN = """tema: {topic}

Contribuciones de los especialistas:
{contributions}"""

_synth_prompt = ChatPromptTemplate.from_messages([("system", SYNTH_SYSTEM), ("human", SYNTH_HUMAN)])





ANALYST_SYSTEM = """ Eres un analista de evidencia.
Recibes (1) un resumen de investigacion y (2) metricas calculadas por codigo.
Tu tarea:
1. Evalua la solidez de la evidencia: cuantas fuentes independientes la respaldan.
2. Indica si las fuentes coiniden o se contradicen, citando cada archivo entre corchetes
3. Señala que informacion falta para una conclusion solida
4. Usa SOLO las metricas y el resumen entragados. NO inentes cifras"""

ANALYST_HUMAN = """Tema: {topic}
Resumen de investigacion: {research}
Metricas (calculadas por codigo): {metrics}"""

_analyst_prompt = ChatPromptTemplate.from_messages([("system", ANALYST_SYSTEM), ("human", ANALYST_HUMAN)])




DETAIL_TEXT = {
    "low": "breve: maximo 3 viñetas o 80 palabras por sección",
    "high": "detallado: explica cada hallazgo con sus cifras y su fuente",
}

MAX_TOOL_ROUNDS = 4


def run_researcher(topic: str, feedback: str = "") -> tuple[str, list[dict]]:
    """Devuelve (resumen de hallazgos, referencias consultadas)"""
    found: list[dict] = []

    @tool
    def search_documents(query: str) -> str:
        """Busca fragmentos relevantes en los documentos de investigación.
        Devuelve el texto de cada fragmento precedido por el archivo del que viene"""
        sources = search(query, k=4)
        found.extend({"file": s.file, "excerpt": s.excerpt} for s in sources)
        return format_context(sources)

    llm = get_llm(temperature=0).bind_tools([search_documents])
    pedido = f"Investiga el siguiente tema: {topic}"
    if feedback:
        pedido += f"\n\nCorrección pedida por el revisor humano: {feedback}"

    messages = [SystemMessage(RESEARCHER_SYSTEM), HumanMessage(pedido)]

    ai = None
    for _ in range(MAX_TOOL_ROUNDS):
        ai = llm.invoke(messages)
        messages.append(ai)
        if not ai.tool_calls:
            break
        for call in ai.tool_calls:
            resultado = search_documents.invoke(call["args"])
            messages.append(ToolMessage(content=resultado, tool_call_id=call["id"]))

    unicas = list({(r["file"], r["excerpt"]): r for r in found}.values())
    return ai.content, unicas



def researcher_node(state: ResearchState) -> dict:
    rev = state.get("revision", 0)
    resumen, refs = run_researcher(state["topic"], state.get("feedback",""))
    return{
        "contributions": [{"agent": "researcher", "content": resumen, "revision": rev}],
        "references": [{**r, "revision": rev} for r in refs]
    }



def synthesizer_node(state: ResearchState) -> dict:
    contribuciones = "\n\n".join(
        f"## {c['agent']}\n{c['content']}" for c in state.get("contributions", [])
    )
    chain = _synth_prompt | get_llm(temperature=0.2)
    respuesta = chain.invoke(
        {
            "sections": ", ".join(state.get("sections", ["hallazgos", "recomendaciones"])),
            "detail": DETAIL_TEXT.get(state.get("detail_level", "low"), DETAIL_TEXT["low"]),
            "topic": state["topic"],
            "contributions": contribuciones,
        }
    )
    return {
        "draft": respuesta.content,
        "contributions": [{"agent": "synthesizer", "content": "Borrador redactado."}],
    }

def analyze_evidence(references: list[dict]) -> dict:
    """Mide la evidencia con codigo deterministico (sin LLM)"""
    por_archivo = Counter(r["file"] for r in references)
    porcentajes: dict[str, list[str]] = {}
    for r in references:
        encontrados = re.findall(r"\d+(?:[.,]\d+)?\s?%", r["excerpt"])
        if encontrados:
            porcentajes.setdefault(r["file"], []).extend(encontrados)
    return {
        "num_fragmentos": len(references),
        "num_archivos": len(por_archivo),
        "fragmentos_por_archivo": dict(por_archivo),
        "porcentajes_por_archivo": porcentajes,
        "palabras_totales": sum(len(r["excerpt"].split()) for r in references),
    }

def analyst_node(state: ResearchState) -> dict:
    rev = state.get("revision", 0)
    research = "\n\n".join( c["content"] for c in 
    current(state.get("contributions", []), state) if c["agent"] == "researcher")
    refs = current(state.get("references", []), state)
    metrics = analyze_evidence(refs)

    chain = _analyst_prompt | get_llm(temperature=0)
    respuesta = chain.invoke({"topic": state["topic"], "research": research, "metrics": metrics})
    return {"contributions": [{"agent": "analyst", "content": respuesta.content, "revision": rev}]}
    


    
    
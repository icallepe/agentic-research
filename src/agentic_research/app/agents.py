import json
import re
from collections import Counter

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from agentic_research.app.config import K_BUSQUEDA
from agentic_research.app.core.ports import Retriever
from agentic_research.app.llm import get_llm
from agentic_research.app.qa import format_context
from agentic_research.app.state import ResearchState, current
from agentic_research.app.stats import cargar_quejas, contar_por_tema

RESEARCHER_SYSTEM = """ Eres un investigador de quejas de clientes de servicios financieros finacieros.
Tienes dos herramientas: 
- search_documents: busca quejas relevnates (textos en ingles escritos por clientes)
-contar_quejas: cuenta cuentas quejas hay por tema en toda la muestra.
Reglas:
-Primero llama a contar_quejas para saber cuales son los temas mas frecuentes.
-Luego haz entre 2 y 3 busquedas con search_documents para entender cada tema principal
-Toda cifra o porcentaje debe venir de contar_quejas. Nunca calcules ni estimes cifras tu.
-Cita cada queja entre corchetes con su identificador, por ejemplo [queja 1233432]
-Cuando cites loq ue dice un cliente, copia una frase corta en ingles entre comillas y explica en español
-Lo que dicen en las quejas es lo que reportan los clientes, no hechos comprobados sobre la empresa.
-Si no enceuntras información relvante, dilo. No inventes datos."""




SYNTH_SYSTEM = """Eres un redactor de informes de producti. Escribes SOLO con la informacion de las contribuciones recibidas.
Reglas:
- Estructura el informe con estas secciones, en este orden: {sections}
- Añade al final una sección "Incertidumbres" con lo que falta o es debil.
- Cita la fuente de cada afirmación entre corchetes, por ejemplo [queja 12345].
- Las cifras y porcentajes deben aparecer tal cual en las contribuciones. Nunca inventes cifras ni fuentes.
- Presenta las qejas como lo que reportan los clientes, no como hechos probados sobre la empresa.
- Nivel de detalle: {detail}"""


SYNTH_HUMAN = """tema: {topic}

Contribuciones de los especialistas:
{contributions}
{feedback_block}"""

_synth_prompt = ChatPromptTemplate.from_messages([("system", SYNTH_SYSTEM), ("human", SYNTH_HUMAN)])


ANALYST_SYSTEM = """ Eres un analista de friccion de prodcto. Recibes (1) un resumen de investigacion sobre quejas de clientes y (2) metricas calculadas por tu codigo.
Tu tarea:
1. Agrupa las quejas en las causas prinicipales de fricción (Maximo 5), ordenadas de una mas a menos frecuente segun las cifras y resumen.
2. Para cada causa, indica cuantas quejas la respaldan y cita al menos una queja como [queja 12345]
3. Indica que tan solida es la evidencia: una causa respalda por pocas quejas es debil.
4. Señala que informacion falta para decidir.
5. Usa SOLO el reusmen y las metricas entregados. No inventes cifras. Recuerda que son relatos de clientes, no ehchos comprobados"""

ANALYST_HUMAN = """Tema: {topic}
Resumen de investigacion: {research}
Metricas (calculadas por codigo): {metrics}"""

_analyst_prompt = ChatPromptTemplate.from_messages([("system", ANALYST_SYSTEM), ("human", ANALYST_HUMAN)])




DETAIL_TEXT = {
    "low": "breve: maximo 3 viñetas o 80 palabras por sección",
    "high": "detallado: explica cada hallazgo con sus cifras y su fuente",
}

MAX_TOOL_ROUNDS = 4



@tool
def contar_quejas(empresa: str = "", desde: str = "") -> str:
    """Cuenta cuantas quejas hay por tema en toda la muestra.
    Usa esta herramienta para cualquier cifra o porcentaje.
    empresa:parte del nombre de la empresa (opcional). desde: fecha AAAA-MM-DD(opcional)"""
    resultado = contar_por_tema(cargar_quejas(), empresa=empresa, desde=desde)
    return json.dumps(resultado, ensure_ascii=False)

def run_researcher(topic: str, retriever: Retriever, feedback: str ="") ->tuple[str, list[dict]]:
    found: list[dict] = []

    @tool
    def search_documents(query: str) -> str:
        """Busca fragmentos relevantes en los documentos de investigación.
        Devuelve el texto de cada fragmento precedido por el archivo del que viene"""
        sources = retriever.search(query, k=K_BUSQUEDA)
        found.extend({"file": s.file, "excerpt": s.excerpt} for s in sources)
        return format_context(sources)

    herramientas = {"search_documents": search_documents, "contar_quejas": contar_quejas}
    llm = get_llm(temperature=0).bind_tools(list(herramientas.values()))

    pedido = f"Investiga este tema: {topic}"
    if feedback:
        pedido += f"\n\nCorrección pedida por el revisor humano (tenla en cuenta): {feedback}"

    messages = [SystemMessage(RESEARCHER_SYSTEM), HumanMessage(pedido)]

    ai = None
    for _ in range(MAX_TOOL_ROUNDS):
        ai = llm.invoke(messages)
        messages.append(ai)
        if not ai.tool_calls:
            break
        for call in ai.tool_calls:
            resultado = herramientas[call["name"]].invoke(call["args"])
            messages.append(ToolMessage(content=resultado, tool_call_id=call["id"]))

    unicas = list({(r["file"], r["excerpt"]): r for r in found}.values())
    return ai.content, unicas



def make_research_node(retriever: Retriever):
    def researcher_node(state: ResearchState) -> dict:
        rev = state.get("revision", 0)
        resumen, refs = run_researcher(state["topic"], retriever, state.get("feedback", ""))
        return {
            "contributions": [{"agent": "researcher", "content": resumen, "revision": rev}], "references": [{**r, "revision": rev} for r in refs],
        }
    return researcher_node

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
            "feedback_block": (
                f"\nCorrección pedida por el revisor humano (debe reflejarse en el informe): "
                f"{state['feedback']}"
                if state.get("feedback")
                else""
            ),
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
    


    
    
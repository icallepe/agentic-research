from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from agentic_research.app.agents import analyst_node, make_research_node, synthesizer_node
from agentic_research.app.core.ports import Retriever
from agentic_research.app.infraestructure.chroma_retriever import ChromaRetriever
from agentic_research.app.state import ResearchState, current
from agentic_research.app.supervisor_brain import decide_route

MAX_STEPS = 8


def initial_state(topic: str, sections: list[str], detail_level: str) -> dict:
    return{
        "topic": topic,
        "sections": sections,
        "detail_level": detail_level,
        "contributions": [],
        "references": [],
        "delegation_trace": [],
        "step_count": 0,
        "revision": 0,
    }


def build_simple_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("researcher", make_research_node(ChromaRetriever()))
    builder.add_node("synthesizer", synthesizer_node)

    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", "synthesizer")
    builder.add_edge("synthesizer", END)
    return builder.compile()

def _has(state: ResearchState, agent: str) -> bool:
    return any(c["agent"] == agent for c in current(state.get("contributions", []), state))

def apply_rules(llm_next: str, has_r: bool, has_a: bool, has_d: bool) -> tuple [str, str]:
    """Reglas de codigo que corrigen al LLM. Devuelve (ruta_final, nota)"""
    if has_d:
        nota = "" if llm_next == "finish" else "regla: ya hay borrador, se termina"
        return "finish", nota
    if not has_r:
        nota = ""if llm_next == "researcher" else "regla: sin investigacion solo puede actuar researcher"
        return "researcher", nota
    if llm_next in ("researcher", "finish"):
        return("synthesizer" if has_a else "analyst"), f"regla: '{llm_next}' no es valido ahora"
    if llm_next == "analyst" and has_a:
        return "synthesizer", "regla: el analisis ya existe"
    return llm_next, ""


def forced_route(has_r: bool, has_d: bool) -> str:
    """Que hacer al llegar al limite de pasos"""
    if has_d:
        return "finish"
    return "synthesizer" if has_r else "finish"


def supervisor(state: ResearchState) -> dict:
    steps = state.get("step_count", 0)
    has_r, has_a = _has(state, "researcher"), _has(state, "analyst")
    has_d = bool(state.get("draft"))

    if steps >= MAX_STEPS:
        route = forced_route(has_r, has_d) if steps == MAX_STEPS else "finish"
        reason = f"limite de {MAX_STEPS} pasos alcanzados"
        llm_next = "(no consultado)"
    else:
        decision = decide_route(
            topic=state["topic"], has_research=has_r, has_analysis=has_a, has_draft=has_d, step_count=steps,
        )
        route, nota = apply_rules(decision.next, has_r, has_a, has_d)
        llm_next, reason = decision.next, (decision.reason + (f" | {nota}" if  nota else ""))

    return {
        "next_route": route,
        "step_count": steps + 1,
        "delegation_trace": [
            {"step": steps + 1, "route": route, "llm_proposed": llm_next, "reason": reason}
        ],
    }

def route_from_supervisor(state: ResearchState) -> str:
    route = state["next_route"]
    if route == "finish":
        return "review" if state.get("draft") else "end"
    return route


def build_graph(checkpointer=None, retriever: Retriever | None = None):
    retriever = retriever or ChromaRetriever()

    builder = StateGraph(ResearchState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("researcher", make_research_node(retriever))
    builder.add_node("analyst", analyst_node)
    builder.add_node("synthesizer", synthesizer_node)
    builder.add_node("review", review_node)


    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "synthesizer": "synthesizer",
            "review": "review",
            "end": END,
        },
    )

    builder.add_edge("researcher", "supervisor")
    builder.add_edge("analyst", "supervisor")
    builder.add_edge("synthesizer", "supervisor")
    builder.add_conditional_edges("review", route_after_review, {"end": END, "supervisor": "supervisor"})
    return builder.compile(checkpointer=checkpointer)
    
def review_node(state: ResearchState) -> dict:
    decision = interrupt (
        {
            "draft": state["draft"],
            "references": sorted({r["file"] for r in current(state.get("references", []), state)}),
            "sources": [
                {"file": r["file"], "excerpt": r["excerpt"]}
                for r in current(state.get("references", []), state)
            ],
            "revision": state.get("revision", 0),
        }
    )
    if decision.get("action") == "approve":
        return{"approved": True}

    return{
        "approved": False,
        "feedback": decision["feedback"],
        "revision": state.get("revision", 0) + 1,
        "draft": "",
        "step_count": 0,
    }

def route_after_review(state: ResearchState) -> str:
    return "end" if state.get("approved") else "supervisor"

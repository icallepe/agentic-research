from langgraph.graph import END, START, StateGraph

from mi_orquestador.app.agents import researcher_node, synthesizer_node, analyst_node
from mi_orquestador.app.state import ResearchState, current
from mi_orquestador.app.supervisor_brain import decide_route

MAX_STEPS = 8

def build_simple_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("researcher", researcher_node)
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
    return state["next_route"]

def build_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("researcher", researcher_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("synthesizer", synthesizer_node)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "synthesizer": "synthesizer",
            "finish": END,
        },
    )

    builder.add_edge("researcher", "supervisor")
    builder.add_edge("analyst", "supervisor")
    builder.add_edge("synthesizer", "supervisor")
    return builder.compile()
    
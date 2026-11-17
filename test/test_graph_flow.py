import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agentic_research.app import graph as g
from agentic_research.app.models import RouteDecision


def fake_decide(topic, has_research, has_analysis, has_draft, step_count): 
    if not has_research:
        nxt = "researcher"
    elif not has_analysis:
        nxt = "analyst"
    elif not has_draft:
        nxt = "synthesizer"
    else:
        nxt = "finish"
    return RouteDecision(next=nxt, reason="falso")

def fake_researcher_factory(retriever):
    def node(state):
        rev = state.get("revision", 0)
        return{
            "contributions": [{"agent": "researcher", "content": "hallazgos", "revision": rev}],
            "references": [{"file": "a.md", "excerpt": "x", "revision": rev}],
        }
    return node

def fake_analyst(state):
    rev = state.get("revision", 0)
    return{"contributions": [{"agent": "analyst", "content": "analisis", "revision": rev}]}

def fake_synth(state):
    rev = state.get("revision", 0)
    return {"draft": f"borrador r{rev}"}


@pytest.fixture
def grafo(monkeypatch):
    monkeypatch.setattr(g, "decide_route", fake_decide)
    monkeypatch.setattr(g, "make_research_node", fake_researcher_factory)
    monkeypatch.setattr(g, "analyst_node", fake_analyst)
    monkeypatch.setattr(g, "synthesizer_node", fake_synth)
    return g.build_graph(InMemorySaver(), retriever=object())

CONFIG = {"configurable": {"thread_id": "t1"}}

def arrancar(grafo):
    return grafo.invoke(g.initial_state("tema", ["hallazgos"], "low"), CONFIG)

def test_se_pausa_para_revision(grafo):
    resultado = arrancar(grafo)
    assert "__interrupt__" in resultado
    assert grafo.get_state(CONFIG).next == ("review",)

def test_aprobar_terminal_el_flujo(grafo):
    arrancar(grafo)
    grafo.invoke(Command(resume={"action": "approve"}), CONFIG)
    snap = grafo.get_state(CONFIG)
    assert snap.values["approved"] is True
    assert not snap.next

def test_pedir_cambios_crea_nueva_revison(grafo):
    arrancar (grafo)
    grafo.invoke(Command(resume={"action": "changes", "feedback": "mas detalle"}), CONFIG)
    snap = grafo.get_state(CONFIG)
    assert snap.values["revision"] == 1
    assert snap.values["feedback"] == "mas detalle"
    assert snap.values["draft"] == "borrador r1"
    assert snap.next == ("review",)

def test_el_orden_de_los_agentes(grafo):
    arrancar(grafo)
    ruta = [t["route"] for t in grafo.get_state(CONFIG).values["delegation_trace"]]
    assert ruta == ["researcher", "analyst", "synthesizer", "finish"]

def test_sin_borrador_termina_sin_bucle_infinito(monkeypatch):
    """Si el sintetizador falla y no produce borrador, el limite de pasos corta el ciclo"""
    monkeypatch.setattr(g, "decide_route", fake_decide)
    monkeypatch.setattr(g, "make_research_node", fake_researcher_factory)
    monkeypatch.setattr(g, "analyst_node", fake_analyst)
    monkeypatch.setattr(g, "synthesizer_node", lambda state: {})

    grafo = g.build_graph(InMemorySaver(), retriever=object())
    cfg = {"configurable": {"thread_id": "t2"}}
    grafo.invoke(g.initial_state("tema", ["hallazgos"], "low"), cfg)
    snap = grafo.get_state(cfg)
    assert not snap.next
    assert snap.values["step_count"] <= g.MAX_STEPS + 2

    
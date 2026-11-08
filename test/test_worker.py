import asyncio
from types import SimpleNamespace

from agentic_research.app.worker import execute, trace_event
from .fakes import MemoryJobStore


class FakeGraph:
    """Grafo falso: emite unas actualizaciones y termina pausado en la revision."""

    def __init__(self, updates, interrupt=None, values=None):
        self.updates, self.interrupt, self.values = updates, interrupt, values or {}

    async def astream(self, entrada, config, stream_mode):
        for u in self.updates:
            yield u

    async def aget_state(self, config):
        tasks = [SimpleNamespace(interrupts=[SimpleNamespace(value=self.interrupt)])] if self.interrupt else []
        return SimpleNamespace(next=("review",) if self.interrupt else (), tasks=tasks, values=self.values)


SUP = {"supervisor": {"delegation_trace": [{"step": 1, "route": "researcher", "reason": "toca investigar"}]}}


def test_trace_event_traduce_supervisor_y_agentes():
    assert trace_event("supervisor", SUP["supervisor"], 0) == {
        "kind": "supervisor", "step": 1, "route": "researcher", "reason": "toca investigar", "revision": 0,
    }
    assert trace_event("analyst", {}, 1) == {"kind": "agent_done", "agent": "analyst", "revision": 1}
    assert trace_event("review", {}, 0) is None


def test_execute_publica_la_traza_y_devuelve_el_borrador():
    store = MemoryJobStore()
    asyncio.run(store.create({"id": "j1", "status": "running"}))
    payload = {"draft": "# Informe", "references": ["a.md"], "sources": [{"file": "a.md", "excerpt": "x"}], "revision": 0}
    grafo = FakeGraph([SUP, {"researcher": {}}], interrupt=payload)

    result = asyncio.run(execute(grafo, {}, "j1", store, []))

    assert result["status"] == "awaiting_review"
    assert result["sources"] == payload["sources"]
    assert [e["kind"] for e in result["trace"]] == ["supervisor", "agent_done"]
    # la traza ya estaba en el store antes de terminar (la UI la ve en vivo)
    assert len(asyncio.run(store.get("j1"))["trace"]) == 2


def test_execute_sin_borrador_marca_no_results():
    grafo = FakeGraph([SUP], values={"approved": False})
    result = asyncio.run(execute(grafo, {}, "j1"))
    assert result["status"] == "no_results"


def test_execute_aprobado_marca_completed():
    grafo = FakeGraph([], values={"approved": True})
    assert asyncio.run(execute(grafo, {}, "j1"))["status"] == "completed"

import uuid
from contextlib import asynccontextmanager

from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.types import Command

from agentic_research.app.config import REDIS_URL
from agentic_research.app.graph import build_graph, initial_state
from agentic_research.app.models import ResearchRequest


@asynccontextmanager
async def open_graph():
    """Abre la conexion a Redis y entrega el grafo listo para usar"""
    async with AsyncRedisSaver.from_conn_string(
        REDIS_URL, connection_args={"socket_connect_timeout": 30, "socket_timeout": 30}
    ) as saver:
        await saver.asetup()
        yield build_graph(saver)

def _config(thread_id: str) -> dict:
    return{"configurable": {"thread_id": thread_id}}

async def _stream(grafo, entrada, config) -> None:
    async for update in grafo.astream(entrada, config, stream_mode="updates"):
        for nodo, cambios in update.items():
            if nodo == "__interrupt__":
                continue 
            if nodo == "supervisor":
                t = cambios["delegation_trace"][0]
                print(f"[supervisor] paso {t['step']} → {t['route']} ({t['reason']}) ")
            else:
                print(f"[{nodo}] termino")

async def _report(grafo, thread_id: str) -> None:
    snap = await grafo.aget_state(_config(thread_id))
    if snap.next:
        p = snap.tasks[0].interrupts[0].value
        print(f"\n======BORRADOR (revision {p['revision']})==========\n")
        print(p["draft"])
        print("\nReferencias:", ", ".join(p["references"]))
        print(f"\n⏸ ESperando tu revision. thread_id = {thread_id}")
        print(f' Aprobar: uv run agentic-research review {thread_id} --approve')
        print(f'Cambios: uv run agentic-research review {thread_id} --changes "tu comentario"')
    else:
        v = snap.values
        print("\n ✅ Flujo terminado." if v.get("approved") else "\nFlujo terminado sin borrador.")    

async def start_research(topic: str, detail: str) -> None:
    request = ResearchRequest(topic=topic, detail_level=detail)
    thread_id = uuid.uuid4().hex[:8]
    async with open_graph() as grafo:
        estado = initial_state(request.topic, request.sections, request.detail_level)
        await _stream(grafo, estado, _config(thread_id))
        await _report(grafo, thread_id)

async def resume_review(thread_id: str, action: str, feedback: str = "") -> None:
    async with open_graph() as grafo:
        snap = await grafo.aget_state(_config(thread_id))
        if not snap.next:
            print("Ese trabajo no es esperando revision (ya termino o no existe)")
            return
        resume = {"action": action, "feedback": feedback}
        await _stream(grafo, Command(resume=resume), _config(thread_id))
        await _report(grafo, thread_id)

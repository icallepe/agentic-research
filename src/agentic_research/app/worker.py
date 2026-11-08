import asyncio

import redis.asyncio as redis
from langgraph.types import Command

from agentic_research.app.config import REDIS_URL
from agentic_research.app.graph import initial_state
from agentic_research.app.infraestructure.redis_jobs import RedisJobQueue, RedisJobStore
from agentic_research.app.observability import setup_tracing
from agentic_research.app.runner import open_graph


def trace_event(node: str, changes: dict, revision: int) -> dict | None:
    """Convierte una actualizacion del grafo en un evento legible para la UI"""
    if node == "supervisor":
        t = changes["delegation_trace"][0]
        return {
            "kind": "supervisor", "step": t["step"], "route": t["route"],
            "reason": t["reason"], "revision": revision,
        }
    if node in ("researcher", "analyst", "synthesizer"):
        return {"kind": "agent_done", "agent": node, "revision": revision}
    return None


async def execute(grafo, entrada, job_id: str, store=None, trace: list | None = None) -> dict:
    """Ejecuta el grafo hasta que se pause o termine y devuelve los campos del job.

    Si se pasa `store`, publica cada paso en `trace` segun ocurre para que la UI lo muestre en vivo.
    """
    config = {"configurable": {"thread_id": job_id}}
    trace = trace if trace is not None else []
    snap = await grafo.aget_state(config)
    revision = snap.values.get("revision", 0) if snap.values else 0

    async for update in grafo.astream(entrada, config, stream_mode="updates"):
        for node, changes in update.items():
            if node == "review" and "revision" in changes:
                revision = changes["revision"]
            event = trace_event(node, changes, revision)
            if event:
                trace.append(event)
                if store is not None:
                    await store.update(job_id, trace=trace)

    snap = await grafo.aget_state(config)

    if snap.next:
        p = snap.tasks[0].interrupts[0].value
        return {
            "status": "awaiting_review",
            "draft": p["draft"],
            "references": p["references"],
            "sources": p.get("sources", []),
            "revision": p["revision"],
            "trace": trace,
        }
    approved = snap.values.get("approved", False)
    return {"status": "completed" if approved else "no_results", "trace": trace}

async def handle(message: dict, grafo, store) -> None:
    job_id = message["job_id"]
    try:
        job = await store.get(job_id)
        if job is None:
            return
        await store.update(job_id, status="running")

        if message["action"] == "start":
            entrada = initial_state(job["topic"], job["sections"], job["detail_level"])
        else:
            entrada = Command(
                resume={"action": message["review_action"], "feedback": message.get("feedback", "")}
            )
        resultado = await execute(grafo, entrada, job_id, store, list(job.get("trace", [])))
        await store.update(job_id, **resultado)
        print(f"[worker] job {job_id} →  {resultado['status']}")
    except Exception as exc:
        await store.update(job_id, status="failed", error=str(exc))
        print(f"[worker] job{job_id} fallo: {exc}")

async def main() -> None:
    setup_tracing()
    client = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=30, socket_connect_timeout=30)
    store, queue = RedisJobStore(client), RedisJobQueue(client)
    async with open_graph() as grafo:
        print("[worker] listo, esperando trabajos...")
        while True:
            try:
                message = await queue.pop(timeout=5)
            except (redis.RedisError, OSError) as exc:
                print(f"[worker] Redis no responde ({exc}); reintentando...")
                await asyncio.sleep(2)
                continue
            if message is not None:
                await handle(message, grafo, store)

if __name__ == "__main__":
    asyncio.run(main())
    
import asyncio

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from agentic_research.app.graph import build_graph, initial_state

async def main() -> None:
    grafo = build_graph(InMemorySaver())
    config = {"configurable": {"thread_id": "prueba-1"}}

    await grafo.ainvoke(
        initial_state("abandono en el registro de la app", ["hallazgos", "recomendaciones"], "low"),
        config,
    )

    while True:
        snap = await grafo.aget_state(config)
        if not snap.next:
            break
        payload = snap.tasks[0].interrupts[0].value
        print(f"\n=====BORRADOR (revision {payload['revision']}) =====\n{payload['draft']}")
        print("Referencias:", ", ".join(payload["references"]))

        op = input("\n¿Aprobar (a) o pedir cambios (c)?").strip().lower()
        if op == "a":
            resume = {"action": "approve"}
        else:
            resume = {"action": "changes", "feedback": input("¿Que debe cambiar?")}
        await grafo.ainvoke(Command(resume=resume), config)

    print("\nFlujo terminado. Aprobado:", (await grafo.aget_state(config)).values.get("approved"))

asyncio.run(main())

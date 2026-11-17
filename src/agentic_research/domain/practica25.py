from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class Estado(TypedDict, total=False):
    borrador: str
    aprobado: bool

def redactar(state: Estado) -> dict:
    return{"borrador": "Este es el borrador del informe"}

def revisar(state: Estado) -> dict:
    decision = interrupt({"borrador": state["borrador"]})
    return {"aprobado": decision == "si"}

b =  StateGraph(Estado)
b.add_node("redactar", redactar)
b.add_node("revisar", revisar)
b.add_edge(START, "redactar")
b.add_edge("redactar", "revisar")
b.add_edge("revisar", END)

grafo = b.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "demo-1"}}

resultado = grafo.invoke({}, config)
print("Pausado. Mensaje para la persona:", resultado["__interrupt__"][0].value)
print("Siguiente nodo pendiente:", grafo.get_state(config).next)

final = grafo.invoke(Command(resume="si"), config)
print("Resultado final:", final)
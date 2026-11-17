import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class SinReducer(TypedDict):
    notas: list[str]

class ConReducer(TypedDict):
    notas: Annotated[list[str], operator.add]

def agente_a(state) -> dict:
    return{"notas": ["encontre A"]}

def agente_b(state) -> dict:
    return{"notas": ["encontre B"]}

def construir(estado_cls):
    b = StateGraph(estado_cls)
    b.add_node("a", agente_a)
    b.add("b", agente_b)
    b.add_edge(START, "a")
    b.add_edge("a", "b")
    b.add_edge("b", END)
    return b.compile()

print("Sin reducer:", construir(SinReducer).invoke({"notas": []}))
print("Con reducer:", construir(ConReducer).invoke({"notas": []}))

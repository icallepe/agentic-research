from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class Estado(TypedDict):
    texto: str

def poner_maysculas(state: Estado) -> dict:
    return{"texto": state["texto"].upper()}

def agregar_firma(state: Estado) -> dict:
    return{"texto": state["texto"] + " - revisado"}

builder = StateGraph(Estado)
builder.add_node("mayusculas", poner_maysculas)
builder.add_node("firma", agregar_firma)

builder.add_edge(START, "mayusculas")
builder.add_edge("mayusculas", "firma")
builder.add_edge("firma", END)

grafo = builder.compile()

resultado = grafo.invoke({"texto": "hallazgo importante"})
print(resultado)

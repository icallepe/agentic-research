from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class Estado(TypedDict):
    texto: str
    resultado: str

def clasificar(state: Estado) -> dict:
    return{}

def tratar_largo(state: Estado) -> dict:
    return{"resultado": "Texto largo: lo resumiremos"}

def tratar_corto(state: Estado) -> dict:
    return{"resultado": "Texto corto: lo dejamos igual"}

def elegir_camino(state: Estado) -> str:
    return "largo" if len(state["texto"]) > 30 else "corto"

b = StateGraph(Estado)
b.add_node("clasificar", clasificar)
b.add_node("tratar_largo", tratar_largo)
b.add_node("tratar_corto", tratar_corto)

b.add_edge(START, "clasificar")
b.add_conditional_edges(
    "clasificar",
    elegir_camino,
    {"largo": "tratar_largo", "corto": "tratar_corto"},
)
b.add_edge("tratar_largo", END)
b.add_edge("tratar_corto", END)

grafo = b.compile()
print(grafo.invoke({"texto": "hola", "resultado": ""}))
print(grafo.invoke({"texto": "un texto bastante mas largo que treinta caracteres", "resultado": ""}))

print(grafo.get_graph().draw_mermaid())
with open("grafo.mmd", "w", encoding="utf-8") as f:
    f.write(grafo.get_graph().draw_mermaid())
    
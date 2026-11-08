from agentic_research.app.graph import build_graph

grafo = build_graph()
mermaid = grafo.get_graph().draw_mermaid()

with open("grafo.mmd", "w", encoding="utf-8") as f:
    f.write(mermaid)

print(mermaid)

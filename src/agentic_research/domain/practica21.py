from agentic_research.app.graph import build_simple_graph

grafo = build_simple_graph()
print(grafo.get_graph().draw_mermaid())

resultado = grafo.invoke(
    {
        "topic": "abandono en el registro de la app",
        "sections": ["hallazgos", "recomendaciones"],
        "detail_level": "low",
        "contributions": [],
        "references": [],
    }
)

print("\n======= BORRADOR =======\n")
print(resultado["draft"])
print("\nReferencias:", sorted({r["file"] for r in resultado["references"]}))

from agentic_research.app.agents import analyze_evidence

refs = [
    {"file": "analitica.md"," excerpt": "el abandono en este paso es de 41%"},
    {"file": "analitica.md", "excerpt": "Android 52% y iOS 33%,"},
    {"file": "soporte.md", "excerpt": "61% dice que no llega el SMS"},
]

print(analyze_evidence(refs))
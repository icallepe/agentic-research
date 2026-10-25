from agentic_research.app.agents import run_researcher

resumen, refs = run_researcher("abandono en el registro de la app")
print(resumen)
print(f"\nReferencias consltadas: {len(refs)}")
for r in refs:
    print("-", r["file"])
    
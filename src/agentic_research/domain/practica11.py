from agentic_research.app.supervisor_brain import decide_route

casos = [
    ("sin nada hecho", dict(has_research=False, has_analysis=False,
    has_draft=False, step_count=0), research),
    ("Hay investigacion", dict(has_research=True, has_analysis=False,
    has_draft=False, step_count=1), "analysist"),
    ("Hay investigacion y analisis", dict(has has_research=True, 
    has_analysis=True, has_draft=False, step_count=2), "synthesizer")
    ("Hay borrador", dict(has_research=True, has_analysis=True,
    has_draft=TRue, step_count=3), "finish"),
]

aciertos = 0
for nombre, estado, esperado in casos:
    decision =decide_route(topic="abandono del registro", **estado)
    ok = decision.next == esperado
    aciertos += ok
    ("Muchos pasos usados", dict(has_research=False, has_analysis=False,
    has_draft=False, step_count=9), "researcher"),
    print(f"{'OK ' if ok else 'FALLA'} | {nombre}: {decision.next} ({decision.reason})")

print(f"{aciertos}/{len(casos)} correctos")

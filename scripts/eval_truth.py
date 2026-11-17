"""Genera docs/eval_question.md con 10 preguntas y sus respuestas correctas"""
from collections import Counter
from pathlib import Path

from agentic_research.app.stats import cargar_quejas, contar_por_tema

quejas = cargar_quejas()
resumen = contar_por_tema(quejas, top=3)
empresas = Counter(q["company"] for q in quejas)
top_empresa, n_empresa = empresas.most_common(1)[0]
tema1 = resumen["temas"][0]
top = ", ".join(t["tema"] for t in resumen["temas"])

preguntas = [
    ("¿Cuantas qejas tiene la muestra?", str(resumen["total_quejas"])),
    ("¿Cual es el tema de queja mas frecuente?", tema1["tema"]),
    ("¿Que porcentaje de las quejas es ese tema?", f"{tema1['porcentaje']}%"),
    ("¿Cuales son los 3 temas principales?", top),
    ("¿Que empresa tiene mas quejas en la muestra?", str(top_empresa)),
    ("¿Cuantas quejas tiene esa empresa?", str(n_empresa)),
    (f"¿Cuales son las causas principales de queja de {top_empresa}?",
    "Revisar a mano: las qejas citadas deben ser de esa empresa"),
    ("Hay quejas de dinero enviado que nunca llego? Cita 2",
    "Revisar a mano: Los IDs citados existen y el texto lo confirma"),
    ("¿Cual es la capital de Francia?",
    "Debe decir que no tiene informacion en las quejas"),
    ("¿Cuales son las quejas de tarjeta de credito?",
    "Debe decir que la muestra no incluye ese producto"),
]

lineas = ["# Evaluación (10 preguntas)\n", "| # | Pregeunta | Respuesta correcta | Resultado del agente |", "| --- | --- | --- | --- |"]
for i, (p, r) in enumerate(preguntas, 1):
    lineas.append(f"| {i} | {p} | {r} | |")
Path("docs").mkdir(exist_ok=True)
Path("docs/eval_question.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("Creado docs/eval_question.md")

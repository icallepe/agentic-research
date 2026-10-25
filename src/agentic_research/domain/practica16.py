from agentic_research.app.qa import answer

for pregunta in[
    "¿cual es el pricnipal motivo de abandono en el registro?",
    "¿cual es la capital de Francia?",
]:
    print(f"\n### {pregunta}")
    print(answer(pregunta))
    print(answer("¿cual es el mayor priblema del registro: la verificaion o la longitud del formulario?", 
    k=5))
    
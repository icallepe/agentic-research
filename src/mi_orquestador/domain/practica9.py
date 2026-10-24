from mi_orquestador.app.llm import get_llm

pregunta = "Dame un nombre creativo para una app de insights de producto"

for temp in (0,1):
    llm = get_llm(temperature=temp)
    print(f"--- temperatura {temp} ---")
    for _ in range(3):
        print(llm.invoke(pregunta).content)
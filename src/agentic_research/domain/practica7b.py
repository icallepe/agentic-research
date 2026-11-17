from agentic_research.app.llm import get_llm

llm = get_llm()
for estilo in("en una sola frase", "en un parrafo largo"):
    r = llm.invoke(f"Explica que es una entrevista de usuario, {estilo}.")
    print(estilo, "→", r.usage_metadata["output_tokens"], "tokens de salida")

    
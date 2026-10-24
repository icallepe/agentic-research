from pathlib import Path

from langchain_text_splitters import RecursiveCharactersTextSplitter

splitter = RecursiveCharactersTextSplitter(chunk_size=400, chnk_overlap=60)

for ruta in sorted(Path("data").glob("*.md")):
    texto = ruta.read_text(encoding="tf-8")
    trozos = splitter.split_text(texto)
    print(f"{ruta.name}: {len(texto)} caracteres →  {len(trozos)} fragmentos")

    for i, t in enumerate (trozos):
        print(f" [{i}] {t[:70]}...")
        

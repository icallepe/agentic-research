from pathlib import Path

DATA_DIR = Path("data")

def cargar_documentos() -> dict[str, str]:
    """Devuelve {nombre_de_archivo: contenido} de todos los .md en data/."""
    documentos = {}
    for ruta in sorted(DATA_DIR.glob("*.md")):
        documentos[ruta.name] = ruta.read_text(encoding="utf-8")
    return documentos

if __name__ == "__main__":
    docs = cargar_documentos()
    for nombre, contenido in docs.items():
        print(f"{nombre}: {len(contenido.split())} palabras")
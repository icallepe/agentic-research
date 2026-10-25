class Fuente:
    def __init__(self, archivo: str, contenido: str) -> None:
        self.archivo = archivo
        self.contenido = contenido

    def num_palabras(self) -> int:
        return len(self.contenido.split())

    def __repr__(self) -> str:
        return f"Fuente({self.archivo!r}, {self.num_palabras()} palabras)"

    def es_larga(self, minimo: int =100) -> bool:
        return sef.num_palabras() > minimo


f = Fuente("entrevistas.md", "El usuario abandonó el paso dos") 
print(f)
print(f.num_palabras())

print(f.es_larga(3))
print(f.es_larga())
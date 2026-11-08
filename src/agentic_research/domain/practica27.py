from fastapi import FastAPI

app = FastAPI(title="Prueba")

@app.get("/saludo")
def saludo(nombre: str = "mundo"):
    return{"mensaje": f"Hola, {nombre}"}
    
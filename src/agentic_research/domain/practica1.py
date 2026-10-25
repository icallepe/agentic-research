#VARIABLES Y TIPOS
tema = "abandono del registro en la app"   # str: texto
num_entrevistas = 12                       # int: número entero
tasa = 0.35                                # float: número con decimales
publicado = False                          # bool: verdadero o falso

print(f"Tema: {tema} | entrevistas: {num_entrevistas} | tasa: {tasa:.0%}")



#LISTAS Y DICCIONARIOS
secciones = ["hallazgos", "riesgos", "recomendaciones"]   # lista: ordenada
secciones.append("próximos pasos")

fuente = {"archivo": "entrevistas.md", "paginas": 4}      # diccionario: clave -> valor
print(fuente["archivo"])
print(len(secciones))



#BUCLES Y CONDICIONALES
for i, seccion in enumerate(secciones, start=1):
    print(f"{i}. {seccion}")

if num_entrevistas >= 10:
    print("Muestra suficiente")
else:
    print("Faltan entrevistas")



#FUNCIONES
def resumen_fuente(fuente: dict) -> str:
    return f"{fuente['archivo']} ({fuente['paginas']} páginas)"

print(resumen_fuente(fuente))
from pydantic import ValidationError

from agentic_research.app.models import ResearchRequest

#Caso valido
ok = ResearchRequest(topic="abandono al registro")
print(ok)
print(ok.model_dump())   

#caso no valido por detail_level no perimitido
try:
    ResearchRequest(topic="abandono del registro", detail_level="medio")
excerpt ValidationError as e:
    print("Error de validación:")
    print(e)

#caso invalido por tema muy corto
try:
    ResearchRequest(topic="a")
excerpt ValidationError as e:
    print("tema muy corto")

try:
    ResearchRequest(topic="abandono del registro", max_sources=11)
excerpt ValidationError:
    print("max_sources fuera del rango")

    


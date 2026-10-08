import asyncio

from pydantic import ValidationError

from mi_orquestador.domain.models import ResearchRequest
from mi_orquestador.orchestrator import run


def main() -> None:
    request = ResearchRequest(
        topic="Agentes de IA",
        sections=["Introducción", "Estado del arte"],
        detail_level="high",
    )
    asyncio.run(run(request))

    # Prueba con un detail_level inválido para ver el error de Pydantic
    try:
        ResearchRequest(topic="Agentes de IA", sections=[], detail_level="medium")
    except ValidationError as e:
        print(e)

import asyncio

from pydantic import ValidationError


def main() -> None:
    from agentic_research.app.models import ResearchRequest
    from agentic_research.orchestrator import run

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

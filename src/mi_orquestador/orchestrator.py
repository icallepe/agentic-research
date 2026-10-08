import asyncio

from mi_orquestador.domain.models import ResearchRequest


async def run(request: ResearchRequest) -> None:
    await asyncio.sleep(1)
    print(request.topic)

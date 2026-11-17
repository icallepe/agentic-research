from abc import ABC, abstractmethod

from agentic_research.app.models import Source


class Retriever(ABC):
    """Algo que sabe buscar fragmentos relevantes en los documentos"""

    @abstractmethod
    def search  (self, query: str, k: int =2) -> list[Source]: ...

class JobStore(ABC):
    """Donde se guarda el estado de cada job""" 

    @abstractmethod
    async def create(self, job: dict) -> None: ...

    @abstractmethod
    async def get(self, job_id: str) -> dict | None: ...

    @abstractmethod
    async def update(self, job_id: str, **fields) -> None: ...

    @abstractmethod
    async def list(self, limit: int = 50) -> list[dict]:
        """Jobs mas recientes primero"""

    @abstractmethod
    async def transition  (self, job_id: str, expected: str, new: str) -> bool:
        """Cambia el estado SOLO si el actua es 'expected'. Devuelve si lo logro"""
    
class JobQueue(ABC):
    """Cola de tareas pendientes"""

    @abstractmethod
    async def push(self, message: dict) -> None: ...

    @abstractmethod
    async def pop(self, timeout: int = 5) -> dict |None: ...

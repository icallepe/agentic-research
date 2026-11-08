class MemoryJobStore:
    """JobStore en memoria para tests (misma interfaz que RedisJobStore)."""

    def __init__(self) -> None:
        self.jobs: dict[str, dict] = {}

    async def create(self, job: dict) -> None:
        self.jobs[job["id"]] = dict(job)

    async def get(self, job_id: str) -> dict | None:
        job = self.jobs.get(job_id)
        return dict(job) if job else None

    async def update(self, job_id: str, **fields) -> None:
        self.jobs[job_id].update(fields)

    async def list(self, limit: int = 50) -> list[dict]:
        return [dict(j) for j in list(self.jobs.values())[::-1][:limit]]

    async def transition(self, job_id: str, expected: str, new: str) -> bool:
        job = self.jobs.get(job_id)
        if job is None or job.get("status") != expected:
            return False
        job["status"] = new
        return True


class MemoryJobQueue:
    """JobQueue en memoria para tests."""

    def __init__(self) -> None:
        self.messages: list[dict] = []

    async def push(self, message: dict) -> None:
        self.messages.append(message)

    async def pop(self, timeout: int = 5) -> dict | None:
        return self.messages.pop(0) if self.messages else None

import json
import time

from agentic_research.app.core.ports import JobQueue, JobStore

JSON_FIELDS = {"references", "sections", "sources", "trace"}
INT_FIELDS = {"revision"}
FLOAT_FIELDS = {"created_at"}
INDEX_KEY = "jobs:index"


_TRANSITION = """
if redis.call('HGET', KEYS[1], 'status') == ARGV[1] then
    redis.call('HSET', KEYS[1], 'status', ARGV[2])
    return 1
end
return 0"""

def _encode(job: dict) -> dict:
    return {k: json.dumps(v) if k in JSON_FIELDS else str(v) for k, v in job.items()}

def _decode(raw: dict) -> dict:
    out = {}
    for k, v in raw.items():
        if k in JSON_FIELDS:
            out[k] = json.loads(v)
        elif k in INT_FIELDS:
            out[k] = int(v)
        elif k in FLOAT_FIELDS:
            out[k] = float(v)
        else:
            out[k] = v
    return out

class RedisJobStore(JobStore):
    def __init__(self, client) -> None:
        self.r = client

    def _key(self, job_id: str) -> str:
        return f"job:{job_id}"

    async def create(self, job: dict) -> None:
        job = {"created_at": time.time(), **job}
        await self.r.hset(self._key(job["id"]), mapping=_encode(job))
        await self.r.zadd(INDEX_KEY, {job["id"]: job["created_at"]})

    async def get(self, job_id: str) -> dict | None:
        raw = await self.r.hgetall(self._key(job_id))
        return _decode(raw) if raw else None

    async def update(self, job_id: str, **fields) -> None:
        await self.r.hset(self._key(job_id), mapping=_encode(fields))

    async def list(self, limit: int = 50) -> list[dict]:
        ids = await self.r.zrevrange(INDEX_KEY, 0, limit - 1)
        jobs = [await self.get(job_id) for job_id in ids]
        return [j for j in jobs if j is not None]

    async def transition(self, job_id: str, expected: str, new: str) -> bool:
        return bool(await self.r.eval(_TRANSITION, 1, self._key(job_id), expected, new))

class RedisJobQueue(JobQueue):
    KEY = "queue:jobs"

    def __init__(self, client) -> None:
        self.r = client

    async def push(self, message: dict) -> None:
        await self.r.lpush(self.KEY, json.dumps(message))

    async def pop(self, timeout: int = 5) -> dict | None:
        item = await self.r.brpop(self.KEY, timeout=timeout)
        return json.loads(item[1]) if item else None

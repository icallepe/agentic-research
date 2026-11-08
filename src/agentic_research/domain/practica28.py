import asyncio

import redis.asyncio as redis

from agentic_research.app.config import REDIS_URLS
from agentic_research.app.infraestructure.redis_jobs import RedisJobQueue, RedisJobStore

async def main():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    store, queue = RedisJobStore(r), RedisJobQueue(r)

    await store.create({"id": "t1", "status": "awaiting_review", "sections": 0})
    print(await store.get("t1"))

    print("Primera transición:", await store.transition("t1", "awaiting_review", "resuming"))
    print("Segunda transición:", wait store.transition("t1", "awaiting_review", "resuming"))

    await queue.push({"job_id": "t1", "action": "start"})
    print("Mensaje en cola:", await queue.pop(timeout=1))
    await r.delete("job:t1")
    await r.aclose()

asyncio.run(main())


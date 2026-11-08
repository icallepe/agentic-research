import uuid
from pathlib import Path
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI, HTTPException, Query, Request

from agentic_research.app.config import REDIS_URL
from agentic_research.app.infraestructure.redis_jobs import RedisJobQueue, RedisJobStore
from agentic_research.app.models import ResearchRequest, ReviewRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=30)
    app.state.store = RedisJobStore(client)
    app.state.queue = RedisJobQueue(client)
    yield
    await client.aclose()


app = FastAPI(title="Agentic Research", lifespan=lifespan)


def get_store(request: Request):
    return request.app.state.store


def get_queue(request: Request):
    return request.app.state.queue


@app.post("/jobs", status_code=202)
async def create_job(request: ResearchRequest, store=Depends(get_store), queue=Depends(get_queue)) -> dict:
    job_id = uuid.uuid4().hex[:8]
    await store.create(
        {
            "id": job_id,
            "status": "queued",
            "topic": request.topic,
            "sections": request.sections,
            "detail_level": request.detail_level,
            "revision": 0,
        }
    )
    await queue.push({"job_id": job_id, "action": "start"})
    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs")
async def list_jobs(limit: int = Query(50, ge=1, le=200), store=Depends(get_store)) -> list[dict]:
    return await store.list(limit)


@app.get("/jobs/{job_id}")
async def get_job(job_id: str, store=Depends(get_store)) -> dict:
    job = await store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return job


@app.patch("/jobs/{job_id}/review", status_code=202)
async def review_job(
    job_id: str, review: ReviewRequest, store=Depends(get_store), queue=Depends(get_queue)
) -> dict:
    if await store.get(job_id) is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    # Transicion atomica: solo una peticion puede pasar de awaiting_review a resuming
    if not await store.transition(job_id, "awaiting_review", "resuming"):
        raise HTTPException(status_code=409, detail="El job no esta esperando revision")
    await queue.push(
        {
            "job_id": job_id,
            "action": "resume",
            "review_action": review.action,
            "feedback": review.feedback,
        }
    )
    return {"job_id": job_id, "status": "resuming"}


# La interfaz web se sirve desde la misma app (sin CORS). Va al final para no tapar las rutas de la API
app.mount("/", StaticFiles(directory=Path(__file__).parent / "web", html=True), name="web")

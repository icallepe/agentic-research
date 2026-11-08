import asyncio

import pytest
from fastapi.testclient import TestClient

from agentic_research.app.api import app, get_queue, get_store
from .fakes import MemoryJobQueue, MemoryJobStore

@pytest.fixture
def ctx():
    store, queue = MemoryJobStore(), MemoryJobQueue()
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_queue] = lambda: queue
    yield TestClient(app), store, queue
    app.dependency_overrides.clear()

def sembrar(store, job_id="j1", status="awaiting_review"):
    asyncio.run(store.create({"id": job_id, "topic": "tema", "status": status}))

def test_crear_job_lo_guarda_y_lo_encola(ctx):
    client, store, queue = ctx
    r = client.post("/jobs", json={"topic": "abandono en el registro"})
    assert r.status_code == 202
    job_id = r.json()["job_id"]
    assert asyncio.run(store.get(job_id))["status"] == "queued"
    assert queue.messages == [{"job_id": job_id, "action": "start"}]

def test_topic_demasiado_corto_da_422(ctx):
    client, _, _ = ctx
    assert client.post("/jobs", json={"topic": "a"}).status_code == 422

def test_job_inexistente_da_404(ctx):
    client, _, _ = ctx
    assert client.get("/jobs/zzz").status_code == 404

def test_cambios_sin_comentario_da_422(ctx):
    client, store, _ = ctx
    sembrar(store)
    assert client.patch("/jobs/j1/review", json={"action": "changes"}).status_code == 422

def test_revisar_un_job_que_no_espera_revision_da_409(ctx):
    client, store, _ = ctx
    sembrar(store, status="running")
    assert client.patch("/jobs/j1/review", json={"action": "approve"}).status_code == 409

def test_solo_una_revision_gana(ctx):
    client, store, queue = ctx
    sembrar(store)
    primera = client.patch("/jobs/j1/review", json={"action": "approve"})
    segunda = client.patch("/jobs/j1/review", json={"action": "approve"})
    assert primera.status_code == 202
    assert segunda.status_code == 409
    assert len(queue.messages) == 1

def test_listar_jobs_devuelve_los_mas_recientes_primero(ctx):
    client, store, _ = ctx
    sembrar(store, "a")
    sembrar(store, "b")
    r = client.get("/jobs")
    assert r.status_code == 200
    assert [j["id"] for j in r.json()] == ["b", "a"]


def test_listar_jobs_respeta_el_limite(ctx):
    client, store, _ = ctx
    for i in range(3):
        sembrar(store, f"j{i}")
    assert len(client.get("/jobs?limit=2").json()) == 2
    assert client.get("/jobs?limit=0").status_code == 422


def test_la_interfaz_se_sirve_en_la_raiz(ctx):
    client, _, _ = ctx
    r = client.get("/")
    assert r.status_code == 200
    assert "Agentic Research" in r.text
    assert client.get("/app.js").status_code == 200

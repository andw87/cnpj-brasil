"""HTTP interface to test each connector and drive runs (docs/reproduce.md, local test API).

Run:  .venv/Scripts/python -m uvicorn cnpjbench.api.app:app --app-dir src --port 8077
Docs: http://127.0.0.1:8077/docs
"""
from __future__ import annotations

import asyncio
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from pydantic import BaseModel

from .. import __version__
from .. import cnpj as cn
from .. import storage as st
from ..catalog import get_source, load_catalog
from ..connectors import REGISTRY, get_connector
from ..metrics import compute_comparison, compute_run_metrics
from ..runner import fetch_one, make_client, run_collection

app = FastAPI(title="cnpjbench", version=__version__,
              description="Benchmark of free and open-source CNPJ data APIs. One connector per source_id.")


@app.get("/health")
def health() -> dict:
    try:
        st.get_db().command("ping")
        mongo = "ok"
    except Exception as e:  # health must answer even without the database
        mongo = f"unavailable: {type(e).__name__}"
    return {"status": "ok", "version": __version__, "mongo": mongo}


@app.get("/sources")
def sources(status: str | None = None) -> list[dict]:
    return [s.model_dump() | {"connector": s.connector_name, "implemented": s.source_id in REGISTRY}
            for s in load_catalog().values() if status is None or s.status == status]


@app.get("/sources/{source_id}/lookup/{cnpj}")
async def lookup(source_id: str, cnpj: str, raw: bool = Query(False, description="include raw payload")) -> dict:
    """Live single lookup through one connector. Nothing is persisted."""
    try:
        src = get_source(source_id)
        conn = get_connector(src.source_id)
    except KeyError as e:
        raise HTTPException(404, str(e))
    c = cn.normalize(cnpj)
    if not cn.is_valid(c):
        raise HTTPException(422, f"invalid CNPJ check digits: {cnpj}")
    async with make_client() as client:
        r = await fetch_one(client, conn, c)
    body: dict[str, Any] = {"source_id": src.source_id, "telemetry": r["telemetry"],
                            "record": r["record"].to_doc() if r["record"] else None}
    if raw:
        body["payload"] = r["payload"]
    return body


class RunRequest(BaseModel):
    source_id: str
    sample_id: str
    limit: int | None = None
    concurrency: int = 1


@app.post("/runs", status_code=202)
def start_run(req: RunRequest, bg: BackgroundTasks) -> dict:
    src = get_source(req.source_id)
    if src.status != "active":
        raise HTTPException(409, f"{src.source_id} status is {src.status}")
    bg.add_task(lambda: asyncio.run(run_collection(st.get_db(), src.source_id, req.sample_id,
                                                   req.limit, concurrency=req.concurrency)))
    return {"accepted": True, "source_id": src.source_id, "sample_id": req.sample_id}


@app.get("/runs")
def list_runs(source_id: str | None = None, limit: int = 50) -> list[dict]:
    q = {"source_id": source_id.upper()} if source_id else {}
    return list(st.get_db()[st.RUNS].find(q).sort("started_at", -1).limit(limit))


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> dict:
    db = st.get_db()
    run = db[st.RUNS].find_one({"_id": run_id})
    if not run:
        raise HTTPException(404, run_id)
    run["progress"] = {
        "final": db[st.TELEMETRY].count_documents({"run_id": run_id, "final": True}),
        "attempts": db[st.TELEMETRY].count_documents({"run_id": run_id}),
    }
    return run


@app.post("/runs/{run_id}/metrics")
def run_metrics(run_id: str) -> dict:
    try:
        return compute_run_metrics(st.get_db(), run_id)
    except KeyError:
        raise HTTPException(404, run_id)


@app.post("/samples/{sample_id}/comparison")
def comparison(sample_id: str, min_sources: int = 3) -> dict:
    return compute_comparison(st.get_db(), sample_id, min_sources)


@app.get("/samples")
def list_samples() -> list[dict]:
    return list(st.get_db()[st.SAMPLES].find({}, {"cnpjs": 0}).sort("created_at", -1))


@app.get("/seed/stats")
def seed_stats() -> dict:
    db = st.get_db()
    total = db[st.SEED].count_documents({})
    by_state = list(db[st.SEED].aggregate([{"$group": {"_id": "$ref.address_state", "n": {"$sum": 1}}},
                                           {"$sort": {"n": -1}}]))
    return {"total": total,
            "head_office": db[st.SEED].count_documents({"is_head_office": True}),
            "alphanumeric": db[st.SEED].count_documents({"is_alphanumeric": True}),
            "by_state": by_state}

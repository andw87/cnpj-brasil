"""Collection engine (docs/methodology.md, sections 3 and 5).

One run = one source x one sample. Every HTTP attempt writes a telemetry document;
found payloads are kept raw (raw_responses) and normalized (records).
Runs are resumable: CNPJs that already have a final attempt in the run are skipped.
"""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from pymongo.database import Database

from . import storage as st
from .catalog import get_source
from .config import get_settings
from .connectors import get_connector
from .connectors.base import FOUND, NETWORK_ERROR, PARSE_ERROR, RATE_LIMITED, RETRYABLE, TIMEOUT, BaseConnector
from .ratelimit import Pacer


def now() -> datetime:
    return datetime.now(timezone.utc)


def new_run_id(source_id: str) -> str:
    return f"R{now():%Y%m%dT%H%M%S}-{source_id}"


def _backoff(resp: httpx.Response | None, attempt: int) -> float:
    cap = get_settings().max_backoff_s
    if resp is not None:
        for h in ("retry-after", "x-ratelimit-reset"):
            v = resp.headers.get(h)
            if v and v.strip().isdigit() and int(v) < 3600:
                return min(cap, float(v) + 1)
    return min(cap, 5.0 * 2 ** attempt)


async def fetch_one(client: httpx.AsyncClient, conn: BaseConnector, cnpj: str) -> dict[str, Any]:
    """Single attempt. Returns {telemetry, payload, record, resp}; never raises on HTTP issues."""
    ts = now()
    t0 = time.perf_counter()
    resp, payload, record, error = None, None, None, None
    try:
        resp = await client.get(conn.url(cnpj), headers=conn.headers())
        latency = (time.perf_counter() - t0) * 1000
        try:
            payload = resp.json()
        except (json.JSONDecodeError, ValueError):
            payload = None
        outcome = conn.classify(resp, payload)
        if outcome == FOUND:
            try:
                record = conn.parse(cnpj, payload)
            except Exception as e:  # mapping failure is a measured outcome, not a crash
                outcome, error = PARSE_ERROR, f"{type(e).__name__}: {e}"
    except httpx.TimeoutException as e:
        latency, outcome, error = (time.perf_counter() - t0) * 1000, TIMEOUT, type(e).__name__
    except httpx.HTTPError as e:
        latency, outcome, error = (time.perf_counter() - t0) * 1000, NETWORK_ERROR, f"{type(e).__name__}: {e}"
    tel = {
        "source_id": conn.source_id,
        "cnpj": cnpj,
        "ts_start": ts,
        "latency_ms": round(latency, 1),
        "http_status": resp.status_code if resp is not None else None,
        "bytes": len(resp.content) if resp is not None else 0,
        "outcome": outcome,
    }
    if error:
        tel["error"] = error[:300]
    if resp is not None and outcome not in (FOUND, PARSE_ERROR) and resp.content:
        tel["body_head"] = resp.text[:200]          # provider error message (no record data)
    if resp is not None:
        rl = {k: resp.headers[k] for k in resp.headers if "ratelimit" in k.lower() or k.lower() == "retry-after"}
        if rl:
            tel["rate_limit_headers"] = rl
        cache = {k: resp.headers[k] for k in resp.headers
                 if k.lower() in ("cf-cache-status", "x-vercel-cache", "age", "x-cache", "cache-control")}
        if cache:
            tel["cache_headers"] = cache
    return {"telemetry": tel, "payload": payload, "record": record, "resp": resp}


def make_client() -> httpx.AsyncClient:
    s = get_settings()
    return httpx.AsyncClient(timeout=s.http_timeout_s, headers={"User-Agent": s.user_agent},
                             follow_redirects=True)


async def _process(db: Database, run_id: str, conn: BaseConnector, client, pacer: Pacer, cnpj: str,
                   max_retries: int) -> str:
    attempt = 0
    while True:
        await pacer.wait()
        r = await fetch_one(client, conn, cnpj)
        tel = r["telemetry"]
        retry = tel["outcome"] in RETRYABLE and attempt < max_retries
        tel.update(run_id=run_id, attempt=attempt, final=not retry)
        db[st.TELEMETRY].insert_one(tel)
        if not retry:
            break
        wait = _backoff(r["resp"], attempt)
        if tel["outcome"] == RATE_LIMITED:
            pacer.penalize(wait)
        else:
            await asyncio.sleep(wait)
        attempt += 1
    if r["payload"] is not None and tel["outcome"] in (FOUND, PARSE_ERROR):
        db[st.RAW].replace_one({"run_id": run_id, "cnpj": cnpj},
                               {"run_id": run_id, "source_id": conn.source_id, "cnpj": cnpj,
                                "received_at": tel["ts_start"], "payload": r["payload"]}, upsert=True)
    if r["record"] is not None:
        db[st.RECORDS].replace_one({"run_id": run_id, "cnpj": cnpj},
                                   {"run_id": run_id, "source_id": conn.source_id, "cnpj": cnpj,
                                    "data": r["record"].to_doc()}, upsert=True)
    return tel["outcome"]


async def run_collection(db: Database, source_id: str, sample_id: str, limit: int | None = None,
                         run_id: str | None = None, concurrency: int = 1, *, offset: int = 0,
                         label: str | None = None, mode: str = "compliance", rpm_multiplier: float = 1.0,
                         unpaced: bool = False, max_retries: int | None = None,
                         breaker_429: int | None = None, formatted_cnpj: bool = False) -> str:
    """mode: compliance (catalog pace, retries) | ramp (pace x rpm_multiplier) | burst (unpaced).
    breaker_429: stop the run after that many consecutive rate_limited attempts (docs/methodology.md, section 4).
    formatted_cnpj: request the punctuated CNPJ (12.345.678/0001-95, slash URL-encoded) instead of the
    14 characters; a different URL bypasses CDN entries cached for the bare form (retest, docs/methodology.md, section 4)."""
    src = get_source(source_id)
    if src.status != "active":
        raise ValueError(f"{src.source_id} status is {src.status}; only active sources are collected")
    sample = db[st.SAMPLES].find_one({"_id": sample_id})
    if not sample:
        raise KeyError(f"sample {sample_id} not found")
    cnpjs = sample["cnpjs"][offset:offset + limit] if limit else sample["cnpjs"][offset:]
    conn = get_connector(src.source_id)
    conn.formatted_cnpj = formatted_cnpj
    retries = get_settings().max_retries if max_retries is None else max_retries
    rpm = None if unpaced else (src.rate_limit_rpm * rpm_multiplier if src.rate_limit_rpm else None)

    if run_id is None:
        run_id = new_run_id(src.source_id)
        if label:
            run_id = f"{run_id}-{label}"
        db[st.RUNS].insert_one({
            "_id": run_id, "source_id": src.source_id, "sample_id": sample_id, "status": "running",
            "label": label, "mode": mode, "started_at": now(), "planned": len(cnpjs), "offset": offset,
            "config": {"rate_limit_rpm": src.rate_limit_rpm, "rate_limit_basis": src.rate_limit_basis,
                       "paced_rpm": rpm, "rpm_multiplier": None if unpaced else rpm_multiplier,
                       "concurrency": concurrency, "max_retries": retries, "breaker_429": breaker_429,
                       "formatted_cnpj": formatted_cnpj,
                       "timeout_s": get_settings().http_timeout_s, "user_agent": get_settings().user_agent},
        })
    else:
        db[st.RUNS].update_one({"_id": run_id}, {"$set": {"status": "running"},
                                                 "$push": {"resumed_at": now()}})
    done = set(db[st.TELEMETRY].distinct("cnpj", {"run_id": run_id, "final": True}))
    todo = [c for c in cnpjs if c not in done]

    pacer = Pacer(rpm)
    queue: asyncio.Queue[str] = asyncio.Queue()
    for c in todo:
        queue.put_nowait(c)
    streak = {"n": 0, "tripped": False}

    async with make_client() as client:
        async def worker():
            while not queue.empty() and not streak["tripped"]:
                c = queue.get_nowait()
                out = await _process(db, run_id, conn, client, pacer, c, retries)
                streak["n"] = streak["n"] + 1 if out == RATE_LIMITED else 0
                if breaker_429 and streak["n"] >= breaker_429:
                    streak["tripped"] = True

        try:
            await asyncio.gather(*(worker() for _ in range(max(1, concurrency))))
            status = "stopped_breaker" if streak["tripped"] else "finished"
        except BaseException:
            status = "interrupted"
            raise
        finally:
            db[st.RUNS].update_one({"_id": run_id}, {"$set": {"status": status, "finished_at": now()}})
    return run_id

"""MongoDB access, collection names and index definitions (docs/reproduce.md).

Index names follow  <ix|ux>_<collection>__<field>[_<field>...]  (ux = unique).
"""
from __future__ import annotations

from functools import lru_cache

from pymongo import ASCENDING, DESCENDING, IndexModel, MongoClient
from pymongo.database import Database

from .config import get_settings

SEED = "seed_companies"
SAMPLES = "samples"
RUNS = "runs"
TELEMETRY = "telemetry"
RAW = "raw_responses"
RECORDS = "records"
METRICS = "metrics"


def _ix(collection: str, keys: list[tuple[str, int]], unique: bool = False) -> IndexModel:
    name = f"{'ux' if unique else 'ix'}_{collection}__{'_'.join(k for k, _ in keys)}"
    return IndexModel(keys, name=name, unique=unique)


INDEXES: dict[str, list[IndexModel]] = {
    SEED: [
        _ix(SEED, [("ref.address_state", ASCENDING)]),
        _ix(SEED, [("is_head_office", ASCENDING)]),
    ],
    SAMPLES: [_ix(SAMPLES, [("created_at", DESCENDING)])],
    RUNS: [
        _ix(RUNS, [("source_id", ASCENDING), ("started_at", DESCENDING)]),
        _ix(RUNS, [("sample_id", ASCENDING)]),
    ],
    TELEMETRY: [
        _ix(TELEMETRY, [("run_id", ASCENDING), ("cnpj", ASCENDING), ("attempt", ASCENDING)], unique=True),
        _ix(TELEMETRY, [("source_id", ASCENDING), ("outcome", ASCENDING)]),
        _ix(TELEMETRY, [("run_id", ASCENDING), ("ts_start", ASCENDING)]),
    ],
    RAW: [_ix(RAW, [("run_id", ASCENDING), ("cnpj", ASCENDING)], unique=True)],
    RECORDS: [
        _ix(RECORDS, [("run_id", ASCENDING), ("cnpj", ASCENDING)], unique=True),
        _ix(RECORDS, [("cnpj", ASCENDING), ("source_id", ASCENDING)]),
    ],
    METRICS: [_ix(METRICS, [("run_id", ASCENDING), ("metric", ASCENDING)], unique=True)],
}


@lru_cache
def get_db() -> Database:
    s = get_settings()
    return MongoClient(s.mongo_uri, serverSelectionTimeoutMS=5000, tz_aware=True)[s.mongo_db]


def ensure_indexes(db: Database | None = None) -> dict[str, list[str]]:
    db = db if db is not None else get_db()
    return {name: db[name].create_indexes(models) for name, models in INDEXES.items()}

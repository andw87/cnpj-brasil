"""Step 31 — derive a sample from CNPJs that every listed source returned as found (docs/methodology.md, section 4).

Used by wave 2 (saturation): removes not_found noise so 429 behaviour is measured on hits only.
Usage: python scripts/31_derive_sample.py --from-sample SMP-... --labels w1a w1b --size 200 --label w2
Sample ID: SMP-<YYYYMMDD>-n<size>-r<seed>-<label>
"""
import _bootstrap  # noqa: F401

import argparse
import random
from datetime import datetime, timezone

from cnpjbench import storage as st
from cnpjbench.metrics import labeled_runs

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-sample", required=True)
    ap.add_argument("--labels", nargs="+", required=True)
    ap.add_argument("--size", type=int, required=True)
    ap.add_argument("--seed", type=int, default=20261116)
    ap.add_argument("--label", required=True)
    a = ap.parse_args()
    db = st.get_db()
    groups = labeled_runs(db, a.from_sample, a.labels)
    found_sets = [set(db[st.TELEMETRY].distinct("cnpj", {"run_id": {"$in": rids}, "final": True, "outcome": "found"}))
                  for rids in groups.values()]
    eligible = sorted(set.intersection(*found_sets)) if found_sets else []
    if a.size > len(eligible):
        raise SystemExit(f"size {a.size} > eligible {len(eligible)}")
    chosen = random.Random(a.seed).sample(eligible, a.size)
    now = datetime.now(timezone.utc)
    sample_id = f"SMP-{now:%Y%m%d}-n{a.size}-r{a.seed}-{a.label}"
    db[st.SAMPLES].replace_one({"_id": sample_id}, {
        "_id": sample_id, "created_at": now, "method": "simple_random_from_found_by_all_sources",
        "rng": "python.random.Random", "rng_seed": a.seed, "population_size": len(eligible),
        "derived_from": {"sample_id": a.from_sample, "labels": a.labels, "sources": sorted(groups)},
        "size": a.size, "label": a.label, "composition": {}, "cnpjs": chosen,
    }, upsert=True)
    print(sample_id, f"eligible={len(eligible)}")

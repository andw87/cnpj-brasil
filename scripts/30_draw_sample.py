"""Step 30 — draw a reproducible simple random sample from seed_companies (docs/methodology.md, section 4).

Usage: python scripts/30_draw_sample.py --size 1100 --seed 20261116
       python scripts/30_draw_sample.py --size 50 --seed 20261116 --label pilot
Sample ID: SMP-<YYYYMMDD>-n<size>-r<seed>[-<label>]
"""
import _bootstrap  # noqa: F401

import argparse
import random
from collections import Counter
from datetime import datetime, timezone

from cnpjbench import storage as st

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, required=True)
    ap.add_argument("--seed", type=int, default=20261116)
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    db = st.get_db()

    population = sorted(db[st.SEED].distinct("_id"))          # sorted => draw depends only on seed
    if a.size > len(population):
        raise SystemExit(f"size {a.size} > population {len(population)}")
    chosen = random.Random(a.seed).sample(population, a.size)

    now = datetime.now(timezone.utc)
    sample_id = f"SMP-{now:%Y%m%d}-n{a.size}-r{a.seed}" + (f"-{a.label}" if a.label else "")
    docs = list(db[st.SEED].find({"_id": {"$in": chosen}}, {"is_head_office": 1, "ref.address_state": 1}))
    composition = {
        "head_office": sum(d["is_head_office"] for d in docs),
        "with_state": sum("address_state" in d.get("ref", {}) for d in docs),
        "by_state": dict(Counter(d.get("ref", {}).get("address_state", "NA") for d in docs).most_common()),
    }
    db[st.SAMPLES].replace_one({"_id": sample_id}, {
        "_id": sample_id, "created_at": now, "method": "simple_random_without_replacement",
        "rng": "python.random.Random", "rng_seed": a.seed, "population_size": len(population),
        "size": a.size, "label": a.label or None, "composition": composition, "cnpjs": chosen,
    }, upsert=True)
    print(sample_id, composition)

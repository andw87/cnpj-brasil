"""Step 32 — build a synthetic "frontier" sample of the newest CNPJ bases (docs/methodology.md, section 4).

CNPJ base numbers (first 8 digits) are issued in increasing order over time, so the head office
(order 0001) of a base drawn near the highest issued base is a recently opened company. The sample
is stratified: the range [lo, hi) is split into equal strata and `per-stratum` bases are drawn
uniformly at random in each one. Check digits are computed; whether the base exists is unknown
until a source answers, so unused bases (not_found everywhere) are expected.

Usage: python scripts/32_build_frontier_sample.py --lo 66000000 --hi 70400000 --strata 22 --per-stratum 10
Sample ID: SMP-<YYYYMMDD>-n<size>-r<seed>-frontier
"""
import _bootstrap  # noqa: F401

import argparse
import random
from datetime import datetime, timezone

from cnpjbench import storage as st
from cnpjbench.cnpj import head_office_cnpj

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lo", type=int, required=True)
    ap.add_argument("--hi", type=int, required=True)
    ap.add_argument("--strata", type=int, default=22)
    ap.add_argument("--per-stratum", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20261116)
    ap.add_argument("--label", default="frontier")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    width = (a.hi - a.lo) // a.strata
    strata, cnpjs = [], []
    for i in range(a.strata):
        lo = a.lo + i * width
        bases = sorted(rng.sample(range(lo, lo + width), a.per_stratum))
        strata.append({"index": i, "lo": lo, "hi": lo + width})
        cnpjs += [head_office_cnpj(f"{b:08d}") for b in bases]
    now = datetime.now(timezone.utc)
    sample_id = f"SMP-{now:%Y%m%d}-n{len(cnpjs)}-r{a.seed}-{a.label}"
    db = st.get_db()
    db[st.SAMPLES].replace_one({"_id": sample_id}, {
        "_id": sample_id, "created_at": now, "method": "stratified_uniform_cnpj_base_frontier",
        "rng": "python.random.Random", "rng_seed": a.seed, "population_size": a.hi - a.lo,
        "size": len(cnpjs), "label": a.label, "frontier": {"lo": a.lo, "hi": a.hi, "strata": strata},
        "composition": {"head_office": len(cnpjs)}, "cnpjs": cnpjs,
    }, upsert=True)
    print(sample_id)

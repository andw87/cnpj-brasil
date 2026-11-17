"""Step 40 — collect one sample from one or all active sources (docs/methodology.md, sections 3–4).

Usage: python scripts/40_run_collection.py --source S01 --sample SMP-... [--limit 20]
       python scripts/40_run_collection.py --all-active --sample SMP-... --limit 100 --label w1a
       python scripts/40_run_collection.py --all-active --sample SMP-... --offset 100 --limit 200 --label w1b
       python scripts/40_run_collection.py --all-active --sample SMP-... --mode ramp --rpm-multiplier 2 --max-retries 0
       python scripts/40_run_collection.py --all-active --sample SMP-... --mode burst --concurrency 4 --max-retries 0 --breaker-429 10
       python scripts/40_run_collection.py --source S03 --sample SMP-... --resume R20261116T200000-S03
Sources run in parallel; each one is paced by its own rate_limit_rpm (x multiplier) unless burst.
"""
import _bootstrap  # noqa: F401

import argparse
import asyncio

from cnpjbench import storage as st
from cnpjbench.catalog import load_catalog
from cnpjbench.connectors import REGISTRY
from cnpjbench.metrics import compute_run_metrics
from cnpjbench.runner import run_collection


async def main(a):
    db = st.get_db()
    if a.all_active:
        ids = [s.source_id for s in load_catalog().values() if s.status == "active" and s.source_id in REGISTRY]
    else:
        ids = [x.strip().upper() for x in a.source.split(",")]
    kw = dict(offset=a.offset, label=a.label, mode=a.mode, rpm_multiplier=a.rpm_multiplier,
              unpaced=a.mode == "burst", max_retries=a.max_retries, breaker_429=a.breaker_429,
              formatted_cnpj=a.formatted_cnpj)
    results = await asyncio.gather(*(run_collection(db, sid, a.sample, a.limit, a.resume, a.concurrency, **kw)
                                     for sid in ids), return_exceptions=True)
    for sid, rid in zip(ids, results):
        if isinstance(rid, BaseException):
            print(f"{sid} FAILED: {rid!r}")
            continue
        m = compute_run_metrics(db, rid)
        print(f"{sid} {rid} found_rate={m['return']['R2_found_rate']} 429={m['throughput']['T6_rate_limited_share']} "
              f"rpm={m['throughput']['T4_effective_rpm']} p50={m['throughput']['T5_latency_ms']['p50']}ms", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--source", help="one ID or comma-separated IDs")
    g.add_argument("--all-active", action="store_true")
    ap.add_argument("--sample", required=True)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--label", help="wave label stored in the run (e.g. w1a)")
    ap.add_argument("--mode", choices=["compliance", "ramp", "burst"], default="compliance")
    ap.add_argument("--rpm-multiplier", type=float, default=1.0)
    ap.add_argument("--max-retries", type=int)
    ap.add_argument("--breaker-429", type=int)
    ap.add_argument("--resume", help="run_id to resume (single source only)")
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--formatted-cnpj", action="store_true",
                    help="send the punctuated CNPJ (bypasses CDN cache entries of the bare form)")
    asyncio.run(main(ap.parse_args()))

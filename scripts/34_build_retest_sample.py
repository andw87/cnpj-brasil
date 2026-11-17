"""Step 34 — retest sample: CNPJs a source answered not_found while other sources found them.

Re-querying them later separates missing records (not_found again) from intermittent answers
(found on retest). Usage:
  python scripts/34_build_retest_sample.py --from-sample SMP-... --labels w1a w1b --sources S01 S02
Sample ID: SMP-<YYYYMMDD>-n<size>-r0-retest
"""
import _bootstrap  # noqa: F401

import argparse
from datetime import datetime, timezone

from cnpjbench import storage as st
from cnpjbench.metrics import labeled_runs

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-sample", required=True, nargs="+")
    ap.add_argument("--labels", nargs="+", required=True)
    ap.add_argument("--sources", nargs="+", required=True)
    ap.add_argument("--label", default="retest")
    a = ap.parse_args()
    db = st.get_db()
    groups: dict[str, list] = {}
    for sm in a.from_sample:
        for sid, rids in labeled_runs(db, sm, a.labels).items():
            groups.setdefault(sid, []).extend(rids)
    found_any = set()
    for rids in groups.values():
        found_any |= set(db[st.TELEMETRY].distinct("cnpj", {"run_id": {"$in": rids}, "final": True, "outcome": "found"}))
    missed = set()
    for sid in a.sources:
        missed |= set(db[st.TELEMETRY].distinct("cnpj", {"run_id": {"$in": groups[sid]}, "final": True,
                                                          "outcome": "not_found"})) & found_any
    cnpjs = sorted(missed)
    now = datetime.now(timezone.utc)
    sample_id = f"SMP-{now:%Y%m%d}-n{len(cnpjs)}-r0-{a.label}"
    db[st.SAMPLES].replace_one({"_id": sample_id}, {
        "_id": sample_id, "created_at": now, "method": "retest_of_not_found_found_elsewhere",
        "derived_from": {"sample_id": a.from_sample, "labels": a.labels, "sources": a.sources},
        "size": len(cnpjs), "label": a.label, "composition": {}, "cnpjs": cnpjs}, upsert=True)
    print(sample_id)

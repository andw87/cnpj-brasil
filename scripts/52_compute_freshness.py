"""Step 52 — freshness metrics F1–F4 (docs/methodology.md, section 5).

Usage: python scripts/52_compute_freshness.py --samples SMP-...-frontier SMP-...-frontier2 --labels fr
           --age-sample SMP-... --age-labels w1a w1b --alnum-sample SMP-...-alnum
Stores metric "freshness" under run_id FRS:<samples>:<labels> and prints the recall table.
"""
import _bootstrap  # noqa: F401

import argparse

from cnpjbench import storage as st
from cnpjbench.metrics import _store, compute_declared_age, compute_freshness, labeled_runs

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", nargs="+", required=True)
    ap.add_argument("--labels", nargs="+", required=True)
    ap.add_argument("--age-sample")
    ap.add_argument("--age-labels", nargs="*")
    ap.add_argument("--alnum-sample")
    a = ap.parse_args()
    db = st.get_db()
    v = compute_freshness(db, a.samples, a.labels)
    key = f"FRS:{'+'.join(a.samples)}:{'+'.join(a.labels)}"
    if a.age_sample:
        groups = {}
        for sm, labels in ((a.age_sample, a.age_labels), *((s, a.labels) for s in a.samples)):
            for sid, rids in labeled_runs(db, sm, labels).items():
                groups.setdefault(sid, []).extend(rids)
        v["F3_declared_age"] = compute_declared_age(db, groups)
    if a.alnum_sample:
        sample = db[st.SAMPLES].find_one({"_id": a.alnum_sample})
        f4 = {}
        for sid, rids in labeled_runs(db, a.alnum_sample, ["alnum"]).items():
            tel = {t["cnpj"]: t for t in db[st.TELEMETRY].find({"run_id": rids[-1], "final": True})}
            f4[sid] = {c: {"http_status": tel[c]["http_status"], "outcome": tel[c]["outcome"],
                           "message": (tel[c].get("body_head") or "")[:120]} for c in sample["cnpjs"] if c in tel}
        v["F4_alphanumeric"] = f4
    _store(db, key, "freshness", v)
    sids = sorted(v["runs"])
    print("half_month exists " + " ".join(sids))
    for b, row in v["F2_recall_by_half_month"].items():
        print(b, row["exists"], " ".join(f"{x['found']}/{x['closed']}" for x in row["sources"].values()))
    print("F1 newest:", v["F1_newest_opening_date"])
    print("existing/queried:", v["cnpjs_existing"], "/", v["cnpjs_queried"])

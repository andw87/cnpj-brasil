"""Step 90 — consolidated, machine-readable results: results/summary.json.

Reads results/manifest.yaml (which samples/labels form each result set) and the metrics computed by
steps 50/52, computes wave-2 saturation and repeat consistency, and writes one JSON document with
every published number per source, plus catalog facts. Aggregates only; no CNPJ is written.
Usage: python scripts/90_build_summary.py
"""
import _bootstrap  # noqa: F401

import json
from datetime import datetime, timezone

import yaml

from cnpjbench import storage as st
from cnpjbench.catalog import load_catalog
from cnpjbench.config import PROJECT_ROOT
from cnpjbench.metrics import (comparison_key, compute_repeat_consistency, compute_saturation, labeled_runs,
                               wilson)

RESULTS = PROJECT_ROOT / "results"


def clean(d):
    return {k: v for k, v in d.items() if k not in ("_id", "run_id", "metric")}


if __name__ == "__main__":
    db = st.get_db()
    man = yaml.safe_load((RESULTS / "manifest.yaml").read_text(encoding="utf-8"))
    profiles = yaml.safe_load((PROJECT_ROOT / "catalog" / "source_profiles.yaml").read_text(encoding="utf-8"))
    out = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "status": "exploratory benchmark — single collection window, small samples; see docs/methodology.md",
           "manifest": man, "sources": {}}

    # wave 1
    w1 = man["wave1"]
    cmp_ = db[st.METRICS].find_one({"run_id": comparison_key(w1["sample"], w1["labels"]), "metric": "comparison"})
    for sid, v in cmp_["sources"].items():
        m = {d["metric"]: clean(d) for d in db[st.METRICS].find({"run_id": v["run_id"]})}
        r = m["return"]
        oc = r["R1_outcomes"]
        found = oc.get("found", 0)
        answered = found + oc.get("not_found", 0) + oc.get("restricted", 0)  # denominator of R3 coverage
        closed = m["throughput"]["T2_cnpjs_final"]
        out["sources"].setdefault(sid, {})["wave1"] = {
            "runs": cmp_["run_groups"][sid], "cnpjs_closed": closed,
            "coverage": r["R3_coverage"], "coverage_ci95": wilson(found, answered), "outcomes": r["R1_outcomes"],
            "error_rate": r["R4_error_rate"], "QI": v.get("QI"),
            "completeness_mean": v["C2_mean"], "validity_mean": v["Q1_mean"], "agreement_mean": v["A1_mean"],
            "fields": {f: {"fill": m["completeness"]["C1_fill_rate"][f],
                           "relative_completeness": v["C2_relative_completeness"][f],
                           "validity": m["validity"]["Q1_validity"][f],
                           "agreement": v["A1_consensus_agreement"][f]} for f in v["C2_relative_completeness"]},
            "consistency": {k: m["validity"].get(k) for k in ("Q2_mojibake_rate", "Q3_establishment_consistency",
                                                              "Q4_ibge_state_consistency")},
            "reference_agreement": m.get("seed_agreement", {}).get("A2_seed_agreement"),
            "throughput": {k: m["throughput"][k] for k in ("T4_effective_rpm", "T5_latency_ms",
                                                           "T6_rate_limited_share", "T7_retries_per_cnpj",
                                                           "configured_rpm")},
        }

    # wave 2
    w2 = man["wave2"]
    for sid, rids in labeled_runs(db, w2["sample"], w2["ramp_labels"] + w2["burst_labels"]).items():
        steps = {}
        for rid in rids:
            sat = compute_saturation(db, rid)
            steps[sat["label"]] = {"run_id": rid, **sat}
        b1, b2 = steps.get("w2b-r1"), steps.get("w2b-r2")
        rep = compute_repeat_consistency(db, b1["run_id"], b2["run_id"]) if b1 and b2 else None
        out["sources"].setdefault(sid, {})["wave2"] = {"steps": steps, "repeat_consistency": rep}

    # freshness
    fr = man["freshness"]
    doc = db[st.METRICS].find_one({"run_id": f"FRS:{'+'.join(fr['samples'])}:{'+'.join(fr['labels'])}",
                                   "metric": "freshness"})
    if doc:
        doc = clean(doc)
        for sid in doc["runs"]:
            out["sources"].setdefault(sid, {})["freshness"] = {
                "newest_opening_date": doc["F1_newest_opening_date"].get(sid),
                "recall_by_half_month": {b: row["sources"].get(sid) for b, row in doc["F2_recall_by_half_month"].items()},
                "declared_record_age_days": (doc.get("F3_declared_age") or {}).get(sid),
                "alphanumeric_probe": (doc.get("F4_alphanumeric") or {}).get(sid),
            }
        out["freshness_meta"] = {k: doc[k] for k in ("samples", "window_start", "computed_on", "cnpjs_queried",
                                                     "cnpjs_existing")}

    for s in load_catalog().values():
        if s.source_id in out["sources"] or s.status != "active":
            out["sources"].setdefault(s.source_id, {})["catalog"] = {
                **json.loads(s.model_dump_json()), **(profiles.get(s.source_id) or {})}
    out["sources"] = dict(sorted(out["sources"].items()))
    (RESULTS / "summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
                                          encoding="utf-8")
    print(RESULTS / "summary.json")

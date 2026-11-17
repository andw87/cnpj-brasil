"""Step 60 — write the comparison report for one sample to data/reports/<sample_id>.md.

Usage: python scripts/60_build_report.py --sample SMP-...
Requires step 50. The report contains aggregates only (no CNPJ, no names).
"""
import _bootstrap  # noqa: F401

import argparse
from datetime import datetime, timezone

from cnpjbench import storage as st
from cnpjbench.catalog import get_source
from cnpjbench.config import PROJECT_ROOT
from cnpjbench.schema import SCORED_FIELDS


def pct(v):
    return "—" if v is None else f"{100 * v:.1f}%"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True)
    a = ap.parse_args()
    db = st.get_db()
    cmp_ = db[st.METRICS].find_one({"run_id": f"CMP:{a.sample}", "metric": "comparison"})
    if not cmp_:
        raise SystemExit("run scripts/50_compute_metrics.py --sample first")
    sample = db[st.SAMPLES].find_one({"_id": a.sample}, {"cnpjs": 0})
    srcs = sorted(cmp_["sources"].items(), key=lambda kv: -(kv[1].get("QI") or 0))
    m = {sid: {d["metric"]: d for d in db[st.METRICS].find({"run_id": v["run_id"]})} for sid, v in srcs}

    L = [f"# CNPJ benchmark report — {a.sample}", "",
         f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}. Sample: {sample['size']} CNPJs, "
         f"{sample['method']}, seed {sample['rng_seed']}, population {sample['population_size']}.", "",
         "## Summary (ranked by QI)", "",
         "| Source | QI | Coverage R3 | Rel. completeness C2 | Validity Q1 | Consensus A1 | Eff. rpm T4 | p50 ms | p95 ms |",
         "|---|---|---|---|---|---|---|---|---|"]
    for sid, v in srcs:
        t = m[sid]["throughput"]["T5_latency_ms"]
        L.append(f"| {sid} {get_source(sid).name} | {v.get('QI') or '—'} | {pct(v['R3_coverage'])} | "
                 f"{pct(v['C2_mean'])} | {pct(v['Q1_mean'])} | {pct(v['A1_mean'])} | "
                 f"{v['T4_effective_rpm']} | {t['p50']} | {t['p95']} |")
    L += ["", "## Outcomes (final attempt per CNPJ)", "", "| Source | Outcomes | Rate-limited share T6 |", "|---|---|---|"]
    for sid, _ in srcs:
        L.append(f"| {sid} | {m[sid]['return']['R1_outcomes']} | {pct(m[sid]['throughput']['T6_rate_limited_share'])} |")
    L += ["", "## Field completeness C1 / relative C2 / validity Q1 / consensus A1", "",
          "| Field | " + " | ".join(sid for sid, _ in srcs) + " |", "|---" * (len(srcs) + 1) + "|"]
    for f in SCORED_FIELDS:
        cells = []
        for sid, v in srcs:
            cells.append(f"{pct(m[sid]['completeness']['C1_fill_rate'][f])} / {pct(v['C2_relative_completeness'][f])} / "
                         f"{pct(m[sid]['validity']['Q1_validity'][f])} / {pct(v['A1_consensus_agreement'][f])}")
        L.append(f"| {f} | " + " | ".join(cells) + " |")
    a2_fields = list(m[srcs[0][0]]["seed_agreement"]["A2_seed_agreement"]) if srcs else []
    L += ["", "## Agreement with seed reference A2", "",
          "| Source | " + " | ".join(a2_fields) + " |", "|---" * (len(a2_fields) + 1) + "|"]
    for sid, _ in srcs:
        L.append(f"| {sid} | " + " | ".join(pct(x) for x in m[sid]["seed_agreement"]["A2_seed_agreement"].values()) + " |")
    out = PROJECT_ROOT / "data" / "reports" / f"{a.sample}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(out)

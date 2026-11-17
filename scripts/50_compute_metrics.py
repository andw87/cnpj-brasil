"""Step 50 — (re)compute run metrics and the cross-source comparison (docs/methodology.md, section 5).

Usage: python scripts/50_compute_metrics.py --sample SMP-...                    # latest finished run per source
       python scripts/50_compute_metrics.py --sample SMP-... --labels w1a w1b   # wave groups per source
       python scripts/50_compute_metrics.py --run R20261116T200000-S01
"""
import _bootstrap  # noqa: F401

import argparse
import json

from cnpjbench import storage as st
from cnpjbench.metrics import compute_comparison, compute_run_metrics, labeled_runs, latest_runs

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run")
    g.add_argument("--sample")
    ap.add_argument("--labels", nargs="*")
    ap.add_argument("--min-sources", type=int, default=3)
    a = ap.parse_args()
    db = st.get_db()
    if a.run:
        print(json.dumps(compute_run_metrics(db, a.run), indent=1, default=str))
    else:
        groups = (labeled_runs(db, a.sample, a.labels) if a.labels
                  else {sid: [rid] for sid, rid in latest_runs(db, a.sample).items()})
        for rids in groups.values():
            for rid in rids:
                compute_run_metrics(db, rid)
        cmp_ = compute_comparison(db, a.sample, a.min_sources, a.labels)
        for sid, v in sorted(cmp_["sources"].items()):
            print(sid, {k: v[k] for k in ("R3_coverage", "C2_mean", "Q1_mean", "A1_mean", "T4_effective_rpm", "QI")})

"""Step 75 — source comparison datasheet: sources in columns, every measured attribute in rows.

Usage: python scripts/75_build_datasheet.py --sample SMP-... --labels w1a w1b --name wave1
Writes results/<name>/DATASHEET.md (aggregates only). Requires step 50 with the same labels.
"""
import _bootstrap  # noqa: F401

import argparse
from datetime import datetime, timezone

from cnpjbench import storage as st
from cnpjbench.catalog import get_source
from cnpjbench.config import PROJECT_ROOT
from cnpjbench.metrics import comparison_key
from cnpjbench.schema import SCORED_FIELDS


def p(v, d=0):
    return "—" if v is None else f"{100 * v:.{d}f}"


def row(name, cells):
    return f"| {name} | " + " | ".join(str(c) for c in cells) + " |"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True)
    ap.add_argument("--labels", nargs="*")
    ap.add_argument("--name", required=True)
    a = ap.parse_args()
    db = st.get_db()
    cmp_ = db[st.METRICS].find_one({"run_id": comparison_key(a.sample, a.labels), "metric": "comparison"})
    if not cmp_:
        raise SystemExit("run step 50 with the same --labels first")
    sids = sorted(cmp_["sources"])
    v = cmp_["sources"]
    m = {s: {d["metric"]: d for d in db[st.METRICS].find({"run_id": v[s]["run_id"]})} for s in sids}
    src = {s: get_source(s) for s in sids}
    T = lambda s: m[s]["throughput"]  # noqa: E731
    R = lambda s: m[s]["return"]  # noqa: E731
    rank = {s: i + 1 for i, s in enumerate(sorted(sids, key=lambda s: -(v[s].get("QI") or 0)))}

    L = [f"# Source datasheet — {a.name}", "",
         f"Sample `{a.sample}`, waves `{' + '.join(a.labels or ['latest'])}`, "
         f"{cmp_['cnpjs_with_records']} CNPJs with at least one record. "
         f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} by `scripts/75_build_datasheet.py`.",
         "Metric definitions: [docs/methodology.md](../../docs/methodology.md), section 5. Percentages without decimals unless noted.", "",
         "| Attribute | " + " | ".join(sids) + " |", "|---" * (len(sids) + 1) + "|"]

    L.append(row("**1. Identity**", [""] * len(sids)))
    L.append(row("Name", [src[s].name for s in sids]))
    L.append(row("Access", [src[s].access for s in sids]))
    L.append(row("Open source", ["yes" if src[s].open_source else "no" for s in sids]))
    L.append(row("Upstream (declared)", [src[s].upstream for s in sids]))
    L.append(row("Pace used, rpm (basis)", [f"{src[s].rate_limit_rpm:g} ({src[s].rate_limit_basis})" for s in sids]))

    L.append(row("**2. Judgment**", [""] * len(sids)))
    L.append(row("QI (pre-registered index)", [v[s].get("QI") for s in sids]))
    L.append(row("Rank by QI", [rank[s] for s in sids]))

    L.append(row("**3. Return**", [""] * len(sids)))
    L.append(row("CNPJs closed (T2)", [T(s)["T2_cnpjs_final"] for s in sids]))
    L.append(row("Found rate % (R2)", [p(R(s)["R2_found_rate"], 1) for s in sids]))
    L.append(row("Coverage % (R3)", [p(R(s)["R3_coverage"], 1) for s in sids]))
    L.append(row("Error rate % (R4)", [p(R(s)["R4_error_rate"], 1) for s in sids]))
    L.append(row("Final outcomes (R1)", ["<br>".join(f"{k}: {n}" for k, n in sorted(R(s)["R1_outcomes"].items())) for s in sids]))

    L.append(row("**4. Fields** — fill % / agreement % (C1 / A1); † validity < 99% (Q1 in brackets)", [""] * len(sids)))
    for f in SCORED_FIELDS:
        cells = []
        for s in sids:
            c1 = m[s]["completeness"]["C1_fill_rate"][f]
            a1 = v[s]["A1_consensus_agreement"][f]
            q1 = m[s]["validity"]["Q1_validity"][f]
            if not c1:
                cells.append("not returned")
                continue
            cell = f"{p(c1)} / {p(a1)}"
            if q1 is not None and q1 < 0.99:
                cell += f" † [{p(q1)}]"
            cells.append(cell)
        L.append(row(f"`{f}`", cells))
    L.append(row("Mean fill % (C1)", [p(m[s]["completeness"]["C1_mean"], 1) for s in sids]))
    L.append(row("Mean relative completeness % (C2)", [p(v[s]["C2_mean"], 1) for s in sids]))
    L.append(row("Mean validity % (Q1)", [p(v[s]["Q1_mean"], 1) for s in sids]))
    L.append(row("Mean agreement % (A1)", [p(v[s]["A1_mean"], 1) for s in sids]))

    L.append(row("**5. Time**", [""] * len(sids)))
    L.append(row("Latency p50 ms", [f"{T(s)['T5_latency_ms']['p50']:.0f}" for s in sids]))
    L.append(row("Latency p95 ms", [f"{T(s)['T5_latency_ms']['p95']:.0f}" for s in sids]))
    L.append(row("Latency p99 ms", [f"{T(s)['T5_latency_ms']['p99']:.0f}" for s in sids]))
    L.append(row("Effective rpm (T4)", [T(s)["T4_effective_rpm"] for s in sids]))
    L.append(row("Wall time min (T3)", [f"{T(s)['T3_wall_time_s'] / 60:.1f}" for s in sids]))
    L.append(row("Attempts (T1)", [T(s)["T1_attempts"] for s in sids]))
    L.append(row("HTTP 429 share % (T6)", [p(T(s)["T6_rate_limited_share"], 1) for s in sids]))
    L.append(row("Retries per CNPJ (T7)", [T(s)["T7_retries_per_cnpj"] for s in sids]))

    L.append(row("**6. Consistency**", [""] * len(sids)))
    L.append(row("Broken encoding % of text values (Q2)", [p(m[s]["validity"]["Q2_mojibake_rate"], 2) for s in sids]))
    L.append(row("Head office/branch vs CNPJ % (Q3)", [p(m[s]["validity"]["Q3_establishment_consistency"], 1) for s in sids]))
    L.append(row("IBGE code vs UF % (Q4)", [p(m[s]["validity"]["Q4_ibge_state_consistency"], 1) for s in sids]))
    for f, n in m[sids[0]]["seed_agreement"]["A2_pairs"].items():
        L.append(row(f"Agrees with internal reference: `{f}` % (A2)",
                     [f"{p(m[s]['seed_agreement']['A2_seed_agreement'][f])} (n={m[s]['seed_agreement']['A2_pairs'][f]})"
                      for s in sids]))
    L += ["", "Reading guide: *fill* = share of found records with the field; *agreement* = share of times the "
          "value matches the majority of the other sources holding it (judged only where ≥ 3 sources hold it); "
          "*not returned* = the source never delivered the field. The internal reference is an outdated "
          "registry, so A2 is agreement, not accuracy."]
    out = PROJECT_ROOT / "results" / a.name
    out.mkdir(parents=True, exist_ok=True)
    (out / "DATASHEET.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(out / "DATASHEET.md")

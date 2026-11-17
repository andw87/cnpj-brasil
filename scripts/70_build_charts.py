"""Step 70 — publishable charts + results page (aggregates only) under results/<name>/.

Usage: python scripts/70_build_charts.py quality --sample SMP-... --labels w1a w1b --name wave1
       python scripts/70_build_charts.py saturation --sample SMP-...-w2a --burst-sample SMP-...-w2b --name wave2
Requires step 50 (quality) / runs of wave 2 (saturation). Sources are identified by axis labels,
so a single blue hue encodes magnitude (dataviz: identity never by color alone).
"""
import _bootstrap  # noqa: F401

import argparse
import os
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from cnpjbench import storage as st  # noqa: E402
from cnpjbench.catalog import get_source  # noqa: E402
from cnpjbench.config import PROJECT_ROOT  # noqa: E402
from cnpjbench.metrics import comparison_key, compute_saturation  # noqa: E402
from cnpjbench.schema import SCORED_FIELDS  # noqa: E402

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e4e0"
BLUE, BLUE_LIGHT = "#2a78d6", "#86b6ef"
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK,
    "text.color": INK, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "svg.fonttype": "none", "font.family": "DejaVu Sans",
})


SHORT = {"S01": "BrasilAPI", "S02": "Minha Receita", "S03": "ReceitaWS", "S04": "CNPJá Open",
         "S05": "CNPJ.ws", "S06": "OpenCNPJ.org", "S07": "OpenCNPJ.com"}


def label(sid: str) -> str:
    return f"{sid} {SHORT.get(sid, get_source(sid).name.split(' (')[0])}"


def dot_panel(ax, names, values, title, fmt="{:.1f}%", scale=100, xlim=None):
    y = range(len(names))
    vals = [None if v is None else v * scale for v in values]
    ax.hlines(list(y), [xlim[0] if xlim else 0] * len(names), [v or 0 for v in vals], color=GRID, lw=2)
    ax.scatter([v for v in vals if v is not None], [i for i, v in zip(y, vals) if v is not None],
               s=64, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=3)
    for i, v in zip(y, vals):
        if v is not None:
            ax.annotate(fmt.format(v), (v, i), xytext=(7, 0), textcoords="offset points",
                        va="center", fontsize=9, color=INK2)
    ax.set_yticks(list(y), names)
    ax.invert_yaxis()
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=8)
    ax.grid(axis="y", visible=False)
    if xlim:
        ax.set_xlim(*xlim)


def save(fig, out, name):
    fig.savefig(out / name, format="svg", bbox_inches="tight")
    if os.environ.get("CNPJBENCH_PREVIEW_DIR"):   # PNG preview outside the repo, for visual checks
        fig.savefig(os.path.join(os.environ["CNPJBENCH_PREVIEW_DIR"], name.replace(".svg", ".png")),
                    dpi=110, bbox_inches="tight")
    plt.close(fig)


def pct(v):
    return "—" if v is None else f"{100 * v:.1f}%"


def quality(a, db, out):
    key = comparison_key(a.sample, a.labels)
    cmp_ = db[st.METRICS].find_one({"run_id": key, "metric": "comparison"})
    if not cmp_:
        raise SystemExit(f"no comparison {key}; run step 50 with the same labels")
    srcs = sorted(cmp_["sources"].items(), key=lambda kv: -(kv[1].get("QI") or 0))
    sids = [s for s, _ in srcs]
    names = [label(s) for s in sids]
    m = {s: {d["metric"]: d for d in db[st.METRICS].find({"run_id": v["run_id"]})} for s, v in srcs}

    # 1 — quality dimensions (small multiples, one shared y order)
    dims = [("R3_coverage", "Coverage (R3)"), ("C2_mean", "Relative completeness (C2)"),
            ("Q1_mean", "Field validity (Q1)"), ("A1_mean", "Cross-source agreement (A1)")]
    lo = min((v[k] for _, v in srcs for k, _ in dims if v.get(k) is not None), default=0.8)
    xmin = max(0, (int(lo * 20) / 20 - 0.05)) * 100
    fig, axes = plt.subplots(1, 4, figsize=(13, 0.42 * len(sids) + 1.4), sharey=True)
    for ax, (k, t) in zip(axes, dims):
        dot_panel(ax, names, [v.get(k) for _, v in srcs], t, xlim=(xmin, 104))
        ax.set_xlabel("%")
    waves = f", waves {' + '.join(a.labels)}" if a.labels else ""
    fig.suptitle(f"Data quality by source — {cmp_['cnpjs_with_records']} CNPJs{waves}",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, out, "quality_dimensions.svg")

    # 2 — throughput and latency
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 0.42 * len(sids) + 1.4), sharey=True)
    rpm = [m[s]["throughput"]["T4_effective_rpm"] for s in sids]
    dot_panel(a1, names, rpm, "Effective throughput (T4), requests/min — log scale", fmt="{:.1f}", scale=1,
              xlim=(1, max(r or 1 for r in rpm) * 3))
    a1.set_xscale("log")
    for i, s in enumerate(sids):
        lat = m[s]["throughput"]["T5_latency_ms"]
        a2.plot([lat["p50"], lat["p95"]], [i, i], color=BLUE_LIGHT, lw=2, zorder=2)
        a2.scatter([lat["p95"]], [i], s=64, color=BLUE_LIGHT, edgecolor=SURFACE, linewidth=2, zorder=3)
        a2.scatter([lat["p50"]], [i], s=64, color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=4)
        a2.annotate(f"{lat['p50']:.0f} / {lat['p95']:.0f}", (lat["p95"], i), xytext=(7, 0),
                    textcoords="offset points", va="center", fontsize=9, color=INK2)
    a2.set_title("Latency (T5), ms — dark dot p50, light dot p95", loc="left", fontsize=10.5, pad=8)
    a2.grid(axis="y", visible=False)
    a2.set_xlim(0, max(m[s]["throughput"]["T5_latency_ms"]["p95"] for s in sids) * 1.35)
    fig.tight_layout()
    save(fig, out, "throughput_latency.svg")

    # 3 — field completeness heatmap (C2)
    fields = list(SCORED_FIELDS)
    grid = [[(v["C2_relative_completeness"].get(f) or 0) * 100 for _, v in srcs] for f in fields]
    fig, ax = plt.subplots(figsize=(1.25 * len(sids) + 3, 0.34 * len(fields) + 1.6))
    ax.imshow(grid, cmap=SEQ, vmin=0, vmax=100, aspect="auto")
    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=8.5,
                    color=SURFACE if val >= 55 else INK)
    ax.set_xticks(range(len(sids)), sids)
    ax.set_yticks(range(len(fields)), fields)
    ax.tick_params(axis="x", top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("Relative completeness per field (C2, %) — share of CNPJs where any source has the field",
                 loc="left", fontsize=10.5, pad=24)
    fig.tight_layout()
    save(fig, out, "field_completeness.svg")

    # results page
    L = [f"# {a.name} — data quality", "",
         f"Sample `{a.sample}`, waves {', '.join(a.labels or [])}; {cmp_['cnpjs_with_records']} CNPJs with records. "
         f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}. Aggregates only.", "",
         "![quality](quality_dimensions.svg)", "", "![throughput](throughput_latency.svg)", "",
         "![fields](field_completeness.svg)", "",
         "| Source | QI | R3 coverage | C2 completeness | Q1 validity | A1 agreement | T4 rpm | p50 ms | p95 ms | T6 429 share | Outcomes |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s, v in srcs:
        t = m[s]["throughput"]
        L.append(f"| {label(s)} | {v.get('QI') or '—'} | {pct(v['R3_coverage'])} | {pct(v['C2_mean'])} | "
                 f"{pct(v['Q1_mean'])} | {pct(v['A1_mean'])} | {t['T4_effective_rpm']} | "
                 f"{t['T5_latency_ms']['p50']:.0f} | {t['T5_latency_ms']['p95']:.0f} | "
                 f"{pct(t['T6_rate_limited_share'])} | {m[s]['return']['R1_outcomes']} |")
    a2f = list(m[sids[0]]["seed_agreement"]["A2_seed_agreement"])
    L += ["", "Agreement with the internal reference (A2, not ground truth):", "",
          "| Source | " + " | ".join(a2f) + " |", "|---" * (len(a2f) + 1) + "|"]
    for s in sids:
        L.append(f"| {s} | " + " | ".join(pct(x) for x in m[s]["seed_agreement"]["A2_seed_agreement"].values()) + " |")
    (out / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def saturation(a, db, out):
    steps = [("w2a-x1", "1× limit"), ("w2a-x2", "2× limit"), ("w2a-x4", "4× limit"),
             ("w2b-r1", "burst #1"), ("w2b-r2", "burst #2")]
    runs = {}
    for r in db[st.RUNS].find({"sample_id": {"$in": [a.sample, a.burst_sample]},
                               "label": {"$in": [s for s, _ in steps]},
                               "status": {"$in": ["finished", "stopped_breaker"]}}).sort("started_at", 1):
        runs[(r["source_id"], r["label"])] = r["_id"]
    sids = sorted({s for s, _ in runs})
    sat = {k: compute_saturation(db, rid) for k, rid in runs.items()}
    grid = [[(sat.get((s, lab), {}).get("S4_rate_limited_share") or 0) * 100 for lab, _ in steps] for s in sids]
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(sids) + 1.8))
    ax.imshow(grid, cmap=SEQ, vmin=0, vmax=100, aspect="auto")
    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            k = (sids[i], steps[j][0])
            txt = "—" if k not in sat else f"{val:.0f}%"
            ax.text(j, i, txt, ha="center", va="center", fontsize=9, color=SURFACE if val >= 55 else INK)
    ax.set_xticks(range(len(steps)), [t for _, t in steps])
    ax.set_yticks(range(len(sids)), [label(s) for s in sids])
    ax.tick_params(axis="x", top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("Share of requests answered HTTP 429 by request rate", loc="left", fontsize=10.5, pad=24)
    fig.tight_layout()
    save(fig, out, "saturation_429.svg")

    fig, ax = plt.subplots(figsize=(10, 0.42 * len(sids) + 1.6))
    for i, s in enumerate(sids):
        x1, b = sat.get((s, "w2a-x1")), sat.get((s, "w2b-r1"))
        blocked = b and b.get("status") == "stopped_breaker"
        if x1 and x1["S2_found_rpm"]:
            ax.scatter([x1["S2_found_rpm"]], [i], s=64, marker="o", color=BLUE_LIGHT, edgecolor=SURFACE,
                       linewidth=2, zorder=3)
        if b and b["S2_found_rpm"] and not blocked:
            ax.scatter([b["S2_found_rpm"]], [i], s=64, marker="D", color=BLUE, edgecolor=SURFACE, linewidth=2, zorder=3)
            ax.annotate(f"{b['S2_found_rpm']:.0f}/min", (b["S2_found_rpm"], i), xytext=(8, 0),
                        textcoords="offset points", va="center", fontsize=9, color=INK2)
        elif blocked and x1:
            ax.annotate("burst blocked (HTTP 429)", (x1["S2_found_rpm"], i), xytext=(10, 0),
                        textcoords="offset points", va="center", fontsize=9, color=INK2)
    ax.set_xscale("log")
    ax.set_yticks(range(len(sids)), [label(s) for s in sids])
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.set_title("Successful lookups per minute — circle: at catalog limit, diamond: burst (log scale)",
                 loc="left", fontsize=10.5, pad=8)
    fig.tight_layout()
    save(fig, out, "saturation_throughput.svg")

    L = [f"# {a.name} — saturation", "",
         f"Samples `{a.sample}` (ramp) and `{a.burst_sample}` (burst, queried twice). "
         f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}. Aggregates only.", "",
         "![429](saturation_429.svg)", "", "![throughput](saturation_throughput.svg)", "",
         "| Source | Step | Attempted rpm | Found rpm | 429 share | First 429 at attempt | 429 with Retry-After | Rate-limit headers | Other errors | Run status |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for s in sids:
        for lab, t in steps:
            v = sat.get((s, lab))
            if v:
                L.append(f"| {s} | {t} | {v['S1_attempted_rpm']} | {v['S2_found_rpm']} | {pct(v['S4_rate_limited_share'])} | "
                         f"{v['S3_first_429_at_attempt'] if v['S3_first_429_at_attempt'] is not None else '—'} | "
                         f"{pct(v['S5_429_with_retry_after'])} | {', '.join(v['S6_429_header_names']) or '—'} | "
                         f"{v['S7_other_errors'] or '—'} | {v['status']} |")
    rc = {d["run_id"]: d for d in db[st.METRICS].find({"metric": "repeat_consistency"})}
    rows = [(s, rc[runs[(s, "w2b-r2")]]) for s in sids if (s, "w2b-r2") in runs and runs[(s, "w2b-r2")] in rc]
    if rows:
        L += ["", "Repeat consistency (burst #1 vs #2, same CNPJs):", "",
              "| Source | Found in both | Identical record | p50 latency ratio #2/#1 |", "|---|---|---|---|"]
        L += [f"| {s} | {v['S9_found_in_both']} | {pct(v['S10_identical_record_share'])} | {v['S11_latency_p50_ratio']} |"
              for s, v in rows]
    (out / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def freshness(a, db, out):
    """Recall of recently opened companies per half-month of opening date (F2) + F1."""
    import re as _re
    doc = db[st.METRICS].find_one({"metric": "freshness", "run_id": {"$regex": "^FRS:"}, "samples": {"$all": a.samples}},
                                  sort=[("computed_on", -1)])
    if not doc:
        raise SystemExit("run step 52 first")
    bins = [b for b in doc["F2_recall_by_half_month"] if b != "older"]
    sids = sorted(doc["runs"], key=lambda s: (doc["F1_newest_opening_date"].get(s) or ""), reverse=True)
    months = {"04": "Apr", "05": "May", "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov"}
    cols = [f"{months.get(b[5:7], b[5:7])} {'1–15' if b.endswith('a') else '16–'}" for b in bins]
    grid, txt = [], []
    for s in sids:
        row, trow = [], []
        for b in bins:
            c = doc["F2_recall_by_half_month"][b]["sources"].get(s) or {}
            r = c.get("recall")
            row.append(float("nan") if r is None else r * 100)
            trow.append("" if r is None else f"{r * 100:.0f}\n{c['found']}/{c['closed']}")
        grid.append(row)
        txt.append(trow)
    fig, ax = plt.subplots(figsize=(0.82 * len(bins) + 2.6, 0.62 * len(sids) + 1.9))
    ax.imshow(grid, cmap=SEQ, vmin=0, vmax=100, aspect="auto")
    for i, trow in enumerate(txt):
        for j, t in enumerate(trow):
            v = grid[i][j]
            ax.text(j, i, t, ha="center", va="center", fontsize=7.5,
                    color=SURFACE if v == v and v >= 55 else INK)
    ax.set_xticks(range(len(bins)), cols, rotation=0, fontsize=8)
    ax.set_yticks(range(len(sids)), [f"{label(s)}  (newest {doc['F1_newest_opening_date'].get(s) or '—'})" for s in sids])
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel(f"Opening date of the company, 2026 (half-months) — collected {doc['computed_on']}")
    ax.set_title("Freshness: share of recently opened companies each source returns (F2, %; cell = recall, found/queried)",
                 loc="left", fontsize=10.5, pad=10)
    fig.tight_layout()
    save(fig, out, "freshness_recall.svg")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["quality", "saturation", "freshness"])
    ap.add_argument("--samples", nargs="*")
    ap.add_argument("--sample")
    ap.add_argument("--labels", nargs="*")
    ap.add_argument("--burst-sample")
    ap.add_argument("--name", required=True)
    a = ap.parse_args()
    out = PROJECT_ROOT / "results" / a.name
    out.mkdir(parents=True, exist_ok=True)
    {"quality": quality, "saturation": saturation, "freshness": freshness}[a.kind](a, st.get_db(), out)
    print(out)

"""Metric computation (docs/methodology.md, section 5). Metric IDs: T* throughput, R* return, C* completeness,
Q* validity/quality, A* agreement, QI composite index."""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from datetime import date
from difflib import SequenceMatcher
from statistics import mean, quantiles
from typing import Any, Callable

from pymongo.database import Database

from . import cnpj as cn
from . import normalize as n
from . import storage as st
from .connectors.base import FOUND, NOT_FOUND, RATE_LIMITED, RESTRICTED
from .schema import SCORED_FIELDS

UFS = {"AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE",
       "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "EX"}
UF_IBGE = {"RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17", "MA": "21",
           "PI": "22", "CE": "23", "RN": "24", "PB": "25", "PE": "26", "AL": "27", "SE": "28", "BA": "29",
           "MG": "31", "ES": "32", "RJ": "33", "SP": "35", "PR": "41", "SC": "42", "RS": "43", "MS": "50",
           "MT": "51", "GO": "52", "DF": "53"}
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
MOJIBAKE = re.compile(r"�|Ã[\x80-\xbf©§£¡³ºª]|Â[\xa0-\xbf]")
LEGAL_SUFFIX = re.compile(r"\b(LTDA|S\.?/?A|SA|ME|EPP|EIRELI|MEI|SS|SOCIEDADE SIMPLES|EM RECUPERACAO JUDICIAL)\b")


def _date_ok(v: str) -> bool:
    try:
        d = date.fromisoformat(v)
    except (TypeError, ValueError):
        return False
    return date(1800, 1, 1) <= d <= date.today()


VALIDATORS: dict[str, Callable[[Any], bool]] = {
    "legal_name": lambda v: len(v) >= 2 and not MOJIBAKE.search(v),
    "trade_name": lambda v: not MOJIBAKE.search(v),
    "establishment_type": lambda v: v in ("head_office", "branch"),
    "registration_status": lambda v: v in ("active", "suspended", "unfit", "closed", "null"),
    "registration_status_date": _date_ok,
    "opening_date": _date_ok,
    "legal_nature_code": lambda v: bool(re.fullmatch(r"\d{4}", v)),
    "legal_nature": lambda v: not MOJIBAKE.search(v),
    "company_size": lambda v: len(v) >= 2,
    "share_capital": lambda v: isinstance(v, (int, float)) and v >= 0 and math.isfinite(v),
    "main_cnae": lambda v: bool(re.fullmatch(r"\d{7}", v)),
    "secondary_cnaes": lambda v: all(re.fullmatch(r"\d{7}", x) for x in v),
    "address_street": lambda v: not MOJIBAKE.search(v),
    "address_number": lambda v: len(v) <= 20,
    "address_complement": lambda v: not MOJIBAKE.search(v),
    "address_district": lambda v: not MOJIBAKE.search(v),
    "address_city": lambda v: not MOJIBAKE.search(v),
    "address_state": lambda v: v in UFS,
    "address_zip": lambda v: bool(re.fullmatch(r"\d{8}", v)) and v != "00000000",
    "address_city_ibge": lambda v: bool(re.fullmatch(r"\d{7}", v)),
    "phones": lambda v: all(10 <= len(x) <= 11 for x in v),
    "email": lambda v: bool(EMAIL.match(v)),
    "partners": lambda v: all(len(p.get("name", "")) >= 2 for p in v),
    "simples_optant": lambda v: isinstance(v, bool),
    "mei_optant": lambda v: isinstance(v, bool),
}


# -- comparison keys (used by agreement) --------------------------------------------------
def _name_key(v: str) -> str:
    s = re.sub(r"[^A-Z0-9 ]", " ", n.fold(v))
    return re.sub(r"\s+", " ", LEGAL_SUFFIX.sub(" ", s)).strip()


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def size_code(v: str) -> str:
    """Company size (porte) labels differ per provider: 'ME' / 'MICRO EMPRESA' / 'Microempresa (ME)'."""
    k = n.fold(v).replace(" ", "")
    if "EPP" in k or "PEQUENOPORTE" in k:
        return "EPP"
    if k in ("ME", "01") or "MICRO" in k:
        return "ME"
    if "DEMAIS" in k or k in ("05",):
        return "DEMAIS"
    return k


def same(field: str, a: Any, b: Any) -> bool:
    if field == "company_size":
        return size_code(a) == size_code(b)
    if field in ("legal_name", "trade_name", "address_street", "address_district", "address_complement"):
        return similar(_name_key(a), _name_key(b)) >= 0.85
    if field in ("address_city", "legal_nature", "address_number"):
        return _name_key(a) == _name_key(b)
    if field == "share_capital":
        return abs(float(a) - float(b)) < 0.01
    if field in ("secondary_cnaes", "phones"):
        return set(a) == set(b)
    if field == "partners":
        return {_name_key(p["name"]) for p in a} == {_name_key(p["name"]) for p in b}
    if field == "email":
        return str(a).lower() == str(b).lower()
    return a == b


def _pct(x: float, total: float) -> float | None:
    return round(x / total, 4) if total else None


def _store(db: Database, run_id: str, metric: str, value: dict) -> dict:
    doc = {"run_id": run_id, "metric": metric, **value}
    db[st.METRICS].replace_one({"run_id": run_id, "metric": metric}, doc, upsert=True)
    return value


# -- per run -------------------------------------------------------------------------------
def _wall_s(tel: list[dict]) -> float:
    if not tel:
        return 0.0
    first = min(t["ts_start"] for t in tel)
    last = max(tel, key=lambda t: t["ts_start"])
    return max((last["ts_start"] - first).total_seconds() + last["latency_ms"] / 1000, 1e-9)


def compute_run_metrics(db: Database, run_id: str | list[str], key: str | None = None) -> dict[str, dict]:
    """Metrics of one run, or of a group of runs of the same source (stored under `key`).
    For a group, wall time is the sum of each run's wall time."""
    run_ids = [run_id] if isinstance(run_id, str) else list(run_id)
    runs = list(db[st.RUNS].find({"_id": {"$in": run_ids}}))
    if len(runs) != len(run_ids):
        raise KeyError(run_id)
    run, run_id = runs[0], key or run_ids[0]
    tel = list(db[st.TELEMETRY].find({"run_id": {"$in": run_ids}}, {"_id": 0}))
    final = [t for t in tel if t.get("final")]
    recs = [r["data"] for r in db[st.RECORDS].find({"run_id": {"$in": run_ids}}, {"data": 1})]
    out: dict[str, dict] = {}

    # T — throughput
    lat = [t["latency_ms"] for t in tel if t.get("http_status") is not None]
    wall = sum(_wall_s([t for t in tel if t["run_id"] == r]) for r in run_ids)
    q = quantiles(lat, n=100) if len(lat) >= 2 else [lat[0]] * 99 if lat else [None] * 99
    out["throughput"] = _store(db, run_id, "throughput", {
        "T1_attempts": len(tel),
        "T2_cnpjs_final": len(final),
        "T3_wall_time_s": round(wall, 1),
        "T4_effective_rpm": round(len(final) / (wall / 60), 2) if wall else None,
        "T5_latency_ms": {"mean": round(mean(lat), 1) if lat else None, "p50": q[49], "p95": q[94], "p99": q[98]},
        "T6_rate_limited_share": _pct(sum(t["outcome"] == RATE_LIMITED for t in tel), len(tel)),
        "T7_retries_per_cnpj": _pct(len(tel) - len(final), len(final)),
        "configured_rpm": run["config"].get("rate_limit_rpm"),
    })

    # R — return
    oc = Counter(t["outcome"] for t in final)
    out["return"] = _store(db, run_id, "return", {
        "R1_outcomes": dict(oc),
        "R2_found_rate": _pct(oc[FOUND], len(final)),
        "R3_coverage": _pct(oc[FOUND], oc[FOUND] + oc[NOT_FOUND] + oc[RESTRICTED]),
        "R4_error_rate": _pct(len(final) - oc[FOUND] - oc[NOT_FOUND] - oc[RESTRICTED], len(final)),
    })

    # C1 — absolute completeness; Q1 — validity
    fill = {f: sum(1 for r in recs if f in r) for f in SCORED_FIELDS}
    valid = {f: sum(1 for r in recs if f in r and VALIDATORS[f](r[f])) for f in SCORED_FIELDS}
    c1 = {f: _pct(fill[f], len(recs)) for f in SCORED_FIELDS}
    q1 = {f: _pct(valid[f], fill[f]) for f in SCORED_FIELDS}
    out["completeness"] = _store(db, run_id, "completeness", {
        "C1_fill_rate": c1,
        "C1_mean": round(mean(v for v in c1.values() if v is not None), 4) if recs else None,
    })
    q1_vals = [v for v in q1.values() if v is not None]
    # Q3 — establishment type consistent with CNPJ order segment; Q4 — IBGE code consistent with UF
    q3 = [r["establishment_type"] == ("head_office" if cn.is_head_office(r["cnpj"]) else "branch")
          for r in recs if "establishment_type" in r]
    q4 = [r["address_city_ibge"][:2] == UF_IBGE.get(r["address_state"])
          for r in recs if "address_city_ibge" in r and r.get("address_state") in UF_IBGE]
    text_vals = [r[f] for r in recs for f in SCORED_FIELDS if isinstance(r.get(f), str)]
    out["validity"] = _store(db, run_id, "validity", {
        "Q1_validity": q1,
        "Q1_mean": round(mean(q1_vals), 4) if q1_vals else None,
        "Q2_mojibake_rate": _pct(sum(bool(MOJIBAKE.search(v)) for v in text_vals), len(text_vals)),
        "Q3_establishment_consistency": _pct(sum(q3), len(q3)),
        "Q4_ibge_state_consistency": _pct(sum(q4), len(q4)),
    })

    # A2 — agreement with seed reference (internal registry, not ground truth)
    seed = {d["_id"]: d.get("ref", {}) for d in db[st.SEED].find({"_id": {"$in": [r["cnpj"] for r in recs]}})}
    pairs = {"legal_name": [], "address_state": [], "address_city": [], "address_zip": [],
             "address_city_ibge": []}
    for r in recs:
        ref = seed.get(r["cnpj"], {})
        for f in pairs:
            if f in r and f in ref:
                pairs[f].append(same(f, r[f], ref[f]) if f != "legal_name"
                                else similar(_name_key(r[f]), _name_key(ref[f])) >= 0.90)
    out["seed_agreement"] = _store(db, run_id, "seed_agreement",
                                   {"A2_seed_agreement": {f: _pct(sum(v), len(v)) for f, v in pairs.items()},
                                    "A2_pairs": {f: len(v) for f, v in pairs.items()}})
    return out


# -- across sources on one sample ------------------------------------------------------------
def latest_runs(db: Database, sample_id: str) -> dict[str, str]:
    runs = db[st.RUNS].find({"sample_id": sample_id, "status": "finished"}).sort("started_at", 1)
    return {r["source_id"]: r["_id"] for r in runs}


def labeled_runs(db: Database, sample_id: str, labels: list[str]) -> dict[str, list[str]]:
    runs = db[st.RUNS].find({"sample_id": sample_id, "label": {"$in": labels},
                             "status": {"$in": ["finished", "stopped_breaker", "stopped_degraded"]}}).sort("started_at", 1)
    out: dict[str, list[str]] = defaultdict(list)
    for r in runs:
        out[r["source_id"]].append(r["_id"])
    return dict(out)


def comparison_key(sample_id: str, labels: list[str] | None) -> str:
    return f"CMP:{sample_id}" + (f":{'+'.join(labels)}" if labels else "")


def compute_comparison(db: Database, sample_id: str, min_sources: int = 3,
                       labels: list[str] | None = None) -> dict:
    """Cross-source metrics. labels=None: latest finished run per source.
    labels=[...]: every run with those wave labels, grouped per source (group metrics recomputed)."""
    if labels:
        groups = labeled_runs(db, sample_id, labels)
        runs = {}
        for sid, rids in groups.items():
            key = f"GRP:{sample_id}:{'+'.join(labels)}:{sid}"
            compute_run_metrics(db, rids, key=key)
            runs[sid] = key
    else:
        groups = {sid: [rid] for sid, rid in latest_runs(db, sample_id).items()}
        runs = {sid: rids[0] for sid, rids in groups.items()}
    by_cnpj: dict[str, dict[str, dict]] = defaultdict(dict)
    for sid, rids in groups.items():
        for r in db[st.RECORDS].find({"run_id": {"$in": rids}}, {"cnpj": 1, "data": 1}):
            by_cnpj[r["cnpj"]][sid] = r["data"]

    has = defaultdict(lambda: defaultdict(int))       # sid -> field -> count with value
    expected = defaultdict(lambda: defaultdict(int))  # sid -> field -> count expected
    agree = defaultdict(lambda: defaultdict(int))
    judged = defaultdict(lambda: defaultdict(int))
    for cnpj_, per_src in by_cnpj.items():
        for f in SCORED_FIELDS:
            holders = {sid: d[f] for sid, d in per_src.items() if f in d}
            if not holders:
                continue
            for sid in per_src:                                   # C2: expected if any source has it
                expected[sid][f] += 1
                has[sid][f] += sid in holders
            if len(holders) >= min_sources:                       # A1: agreement with majority
                for sid, v in holders.items():
                    peers = [w for s2, w in holders.items() if s2 != sid]
                    judged[sid][f] += 1
                    agree[sid][f] += sum(same(f, v, w) for w in peers) * 2 > len(peers)

    result = {"sample_id": sample_id, "labels": labels, "runs": runs, "run_groups": groups,
              "cnpjs_with_records": len(by_cnpj), "sources": {}}
    for sid, rid in runs.items():
        c2 = {f: _pct(has[sid][f], expected[sid][f]) for f in SCORED_FIELDS}
        a1 = {f: _pct(agree[sid][f], judged[sid][f]) for f in SCORED_FIELDS}
        c2v = [v for v in c2.values() if v is not None]
        a1v = [v for v in a1.values() if v is not None]
        m = {d["metric"]: d for d in db[st.METRICS].find({"run_id": rid})}
        result["sources"][sid] = {
            "run_id": rid,
            "C2_relative_completeness": c2, "C2_mean": round(mean(c2v), 4) if c2v else None,
            "A1_consensus_agreement": a1, "A1_mean": round(mean(a1v), 4) if a1v else None,
            "R3_coverage": m.get("return", {}).get("R3_coverage"),
            "Q1_mean": m.get("validity", {}).get("Q1_mean"),
            "T4_effective_rpm": m.get("throughput", {}).get("T4_effective_rpm"),
        }
    _quality_index(result["sources"])
    ck = comparison_key(sample_id, labels)
    db[st.METRICS].replace_one({"run_id": ck, "metric": "comparison"},
                               {"run_id": ck, "metric": "comparison", **result}, upsert=True)
    return result


# -- saturation (wave 2, docs/methodology.md, section 5) ----------------------------------------------------------
def compute_saturation(db: Database, run_id: str) -> dict:
    """429 behaviour of one run: onset, header usage, achieved request rate."""
    run = db[st.RUNS].find_one({"_id": run_id})
    tel = sorted(db[st.TELEMETRY].find({"run_id": run_id}, {"_id": 0}), key=lambda t: t["ts_start"])
    rl = [t for t in tel if t["outcome"] == RATE_LIMITED]
    first_429 = next((i for i, t in enumerate(tel) if t["outcome"] == RATE_LIMITED), None)
    wall = _wall_s(tel)
    hdr = Counter(k.lower() for t in rl for k in t.get("rate_limit_headers", {}))
    ok = [t for t in tel if t["outcome"] == FOUND]
    value = {
        "S1_attempted_rpm": round(len(tel) / (wall / 60), 2) if tel else None,
        "S2_found_rpm": round(len(ok) / (wall / 60), 2) if tel else None,
        "S3_first_429_at_attempt": first_429,
        "S4_rate_limited_share": _pct(len(rl), len(tel)),
        "S5_429_with_retry_after": _pct(sum("retry-after" in {k.lower() for k in t.get("rate_limit_headers", {})}
                                            for t in rl), len(rl)),
        "S6_429_header_names": dict(hdr),
        "S7_other_errors": dict(Counter(t["outcome"] for t in tel if t["outcome"] not in (FOUND, NOT_FOUND, RATE_LIMITED, RESTRICTED))),
        "S8_latency_p50_found_ms": (quantiles([t["latency_ms"] for t in ok], n=100)[49] if len(ok) >= 2 else
                                    (ok[0]["latency_ms"] if ok else None)),
        "mode": run.get("mode"), "label": run.get("label"), "status": run.get("status"),
        "paced_rpm": run["config"].get("paced_rpm"), "concurrency": run["config"].get("concurrency"),
    }
    return _store(db, run_id, "saturation", value)


def compute_repeat_consistency(db: Database, run_a: str, run_b: str) -> dict:
    """Same CNPJs queried twice: identical canonical record share and latency ratio (cache effect)."""
    ra = {r["cnpj"]: r["data"] for r in db[st.RECORDS].find({"run_id": run_a})}
    rb = {r["cnpj"]: r["data"] for r in db[st.RECORDS].find({"run_id": run_b})}
    both = set(ra) & set(rb)
    la = [t["latency_ms"] for t in db[st.TELEMETRY].find({"run_id": run_a, "outcome": FOUND})]
    lb = [t["latency_ms"] for t in db[st.TELEMETRY].find({"run_id": run_b, "outcome": FOUND})]
    med = lambda xs: quantiles(xs, n=100)[49] if len(xs) >= 2 else (xs[0] if xs else None)  # noqa: E731
    value = {"pair": [run_a, run_b], "S9_found_in_both": len(both),
             "S10_identical_record_share": _pct(sum(ra[c] == rb[c] for c in both), len(both)),
             "S11_latency_p50_ratio": round(med(lb) / med(la), 3) if med(la) and med(lb) else None}
    return _store(db, run_b, "repeat_consistency", value)


QI_WEIGHTS = {"R3_coverage": 0.25, "C2_mean": 0.25, "Q1_mean": 0.20, "A1_mean": 0.20, "T_score": 0.10}


def _quality_index(sources: dict[str, dict]) -> None:
    """QI (pre-registered, docs/methodology.md, section 5). T_score = log10(rpm) scaled to [0,1] over the compared sources."""
    logs = {s: math.log10(v["T4_effective_rpm"]) for s, v in sources.items() if v.get("T4_effective_rpm")}
    lo, hi = (min(logs.values()), max(logs.values())) if logs else (0, 0)
    for s, v in sources.items():
        v["T_score"] = round((logs[s] - lo) / (hi - lo), 4) if s in logs and hi > lo else (1.0 if s in logs else None)
        parts = [(w, v.get(k)) for k, w in QI_WEIGHTS.items()]
        v["QI"] = round(sum(w * x for w, x in parts if x is not None), 4) if all(x is not None for _, x in parts) else None


# -- freshness / currency (docs/methodology.md, section 5) --------------------------------------------------------
def _ts(v: Any):
    from datetime import datetime as _dt
    if not isinstance(v, str) or len(v) < 10:
        return None
    try:
        return _dt.fromisoformat(v.replace("Z", "+00:00")[:26] + ("+00:00" if "+" not in v[10:] and "Z" in v else ""))
    except ValueError:
        try:
            return _dt.fromisoformat(v[:10])
        except ValueError:
            return None


def _half_month(d: str) -> str:
    return f"{d[:7]}-{'a' if int(d[8:10]) <= 15 else 'b'}"


def compute_freshness(db: Database, sample_ids: list[str], labels: list[str], window_start: str = "2026-04-01") -> dict:
    """Frontier samples (scripts/32), pooled. A CNPJ 'exists' when at least one source that queried it
    returned it; its opening date is the most common value among those sources. Recall is computed per
    half-month of opening date (a = days 1-15, b = 16-end) inside [window_start, today].
    F1 newest opening date found; F2 recall per half-month; companies declaring an opening date
    before the window (re-registrations) are counted apart."""
    rec: dict[str, dict[str, dict]] = defaultdict(dict)
    closed: dict[str, set] = defaultdict(set)
    runs: dict[str, list] = defaultdict(list)
    for sm in sample_ids:
        for sid, rids in labeled_runs(db, sm, labels).items():
            runs[sid] += rids
            closed[sid] |= set(db[st.TELEMETRY].distinct("cnpj", {"run_id": {"$in": rids}, "final": True,
                                                                  "outcome": {"$in": [FOUND, NOT_FOUND, RESTRICTED]}}))
            for r in db[st.RECORDS].find({"run_id": {"$in": rids}}, {"cnpj": 1, "data.opening_date": 1}):
                rec[r["cnpj"]][sid] = r["data"]
    queried = set().union(*closed.values()) if closed else set()
    opening = {}
    for c, per in rec.items():
        mc = Counter(d.get("opening_date") for d in per.values() if d.get("opening_date")).most_common(1)
        if mc:
            opening[c] = mc[0][0]
    today = date.today().isoformat()
    bins: dict[str, dict] = defaultdict(lambda: {"exists": 0, "found": Counter(), "closed": Counter()})
    for c, d in opening.items():
        b = _half_month(d) if window_start <= d <= today else "older"
        bins[b]["exists"] += 1
        for sid in runs:
            if c in closed[sid]:
                bins[b]["closed"][sid] += 1
                bins[b]["found"][sid] += sid in rec[c]
    f2 = {}
    for b, v in sorted(bins.items()):
        f2[b] = {"exists": v["exists"], "sources": {}}
        for sid in sorted(runs):
            k, n_ = v["found"][sid], v["closed"][sid]
            f2[b]["sources"][sid] = {"found": k, "closed": n_, "recall": _pct(k, n_), "ci95": wilson(k, n_)}
    newest = {sid: max((d["opening_date"] for c, per in rec.items() for s2, d in per.items()
                        if s2 == sid and d.get("opening_date") and d["opening_date"] >= window_start), default=None)
              for sid in sorted(runs)}
    value = {"samples": sample_ids, "labels": labels, "runs": dict(runs), "window_start": window_start,
             "computed_on": today, "cnpjs_queried": len(queried), "cnpjs_existing": len(rec),
             "F1_newest_opening_date": newest, "F2_recall_by_half_month": f2}
    return _store(db, f"FRS:{'+'.join(sample_ids)}:{'+'.join(labels)}", "freshness", value)


def compute_declared_age(db: Database, run_ids_by_source: dict[str, list[str]]) -> dict:
    """F3: age in days of the provider-declared 'updated at' timestamp at collection time."""
    from .connectors import get_connector
    out = {}
    for sid, rids in run_ids_by_source.items():
        key = get_connector(sid).declared_update_key
        if not key:
            out[sid] = None
            continue
        ages = []
        for r in db[st.RAW].find({"run_id": {"$in": rids}}, {"received_at": 1, f"payload.{key}": 1}):
            t = _ts((r.get("payload") or {}).get(key))
            if t is None:
                continue
            got = r["received_at"].replace(tzinfo=None)
            ages.append((got - t.replace(tzinfo=None)).total_seconds() / 86400)
        ages.sort()
        q = lambda p: round(ages[min(len(ages) - 1, int(p * len(ages)))], 1) if ages else None  # noqa: E731
        out[sid] = {"key": key, "n": len(ages), "p10_days": q(0.10), "p50_days": q(0.5), "p90_days": q(0.9),
                    "max_days": round(ages[-1], 1) if ages else None}
    return out


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Wilson score 95% interval for a proportion k/n."""
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)

"""Step 80 — export the evidence behind a result set.

Published (results/<name>/data/, versioned): CNPJs replaced by HMAC-SHA256 pseudonyms
  runs.csv                one row per run: source, label, mode, pace, timing, status
  telemetry.csv           one row per HTTP attempt
  field_observations.csv  one row per (CNPJ, source, field): present, valid, agrees_with_majority
  SHA256SUMS              checksums of the files above
Local only (data/exports/<name>/, git-ignored): full evidence with real CNPJs
  runs.jsonl, telemetry.jsonl, raw_responses.jsonl, records.jsonl, SHA256SUMS

The HMAC key lives in local/pseudonym_key.txt (created on first use, never versioned).
Usage: python scripts/80_export_artifacts.py --sample SMP-... [SMP-...] --labels w1a w1b --name wave1
"""
import _bootstrap  # noqa: F401

import argparse
import csv
import hashlib
import hmac
import json
import secrets
from collections import defaultdict

from cnpjbench import storage as st
from cnpjbench.config import PROJECT_ROOT
from cnpjbench.metrics import VALIDATORS, labeled_runs, latest_runs, same
from cnpjbench.schema import SCORED_FIELDS

KEY_FILE = PROJECT_ROOT / "local" / "pseudonym_key.txt"


def key() -> bytes:
    if not KEY_FILE.exists():
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_text(secrets.token_hex(32), encoding="utf-8")
    return bytes.fromhex(KEY_FILE.read_text(encoding="utf-8").strip())


def sums(folder):
    lines = [f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}"
             for f in sorted(folder.iterdir()) if f.is_file() and f.name != "SHA256SUMS"]
    (folder / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True, nargs="+")
    ap.add_argument("--labels", nargs="*")
    ap.add_argument("--name", required=True)
    ap.add_argument("--min-sources", type=int, default=3)
    a = ap.parse_args()
    db = st.get_db()
    k = key()
    pid = lambda c: hmac.new(k, c.encode(), hashlib.sha256).hexdigest()[:16]  # noqa: E731
    groups: dict[str, list] = {}
    for sm in a.sample:
        g = (labeled_runs(db, sm, a.labels) if a.labels else {s: [r] for s, r in latest_runs(db, sm).items()})
        for sid, rids in g.items():
            groups.setdefault(sid, []).extend(rids)
    run_ids = [r for rs in groups.values() for r in rs]

    pub = PROJECT_ROOT / "results" / a.name / "data"
    loc = PROJECT_ROOT / "data" / "exports" / a.name
    pub.mkdir(parents=True, exist_ok=True)
    loc.mkdir(parents=True, exist_ok=True)

    runs = list(db[st.RUNS].find({"_id": {"$in": run_ids}}).sort("started_at", 1))
    with (pub / "runs.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["run_id", "source_id", "label", "mode", "paced_rpm", "concurrency", "max_retries",
                    "planned", "started_at", "finished_at", "status"])
        for r in runs:
            c = r["config"]
            w.writerow([r["_id"], r["source_id"], r.get("label"), r.get("mode", "compliance"),
                        c.get("paced_rpm", c.get("rate_limit_rpm")), c["concurrency"], c["max_retries"],
                        r["planned"], r["started_at"].isoformat(), r.get("finished_at") and r["finished_at"].isoformat(),
                        r["status"]])

    tel = list(db[st.TELEMETRY].find({"run_id": {"$in": run_ids}}, {"_id": 0}).sort("ts_start", 1))
    with (pub / "telemetry.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["run_id", "source_id", "cnpj_pid", "attempt", "final", "ts_start", "latency_ms",
                    "http_status", "bytes", "outcome", "retry_after", "cdn_cache"])
        for t in tel:
            ra = next((v for h, v in (t.get("rate_limit_headers") or {}).items() if h.lower() == "retry-after"), "")
            ch = {k.lower(): v for k, v in (t.get("cache_headers") or {}).items()}
            cdn = ch.get("cf-cache-status") or ch.get("x-vercel-cache") or ch.get("x-cache") or ""
            w.writerow([t["run_id"], t["source_id"], pid(t["cnpj"]), t["attempt"], t["final"],
                        t["ts_start"].isoformat(), t["latency_ms"], t["http_status"], t["bytes"], t["outcome"], ra, cdn])

    by_cnpj = defaultdict(dict)
    for sid, rids in groups.items():
        for r in db[st.RECORDS].find({"run_id": {"$in": rids}}, {"cnpj": 1, "data": 1}):
            by_cnpj[r["cnpj"]][sid] = r["data"]
    with (pub / "field_observations.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["cnpj_pid", "source_id", "field", "present", "valid", "agrees_with_majority"])
        for c, per in sorted(by_cnpj.items()):
            for f in SCORED_FIELDS:
                holders = {s: d[f] for s, d in per.items() if f in d}
                for s, d in sorted(per.items()):
                    present = f in d
                    agree = ""
                    if present and len(holders) >= a.min_sources:
                        peers = [x for s2, x in holders.items() if s2 != s]
                        agree = int(sum(same(f, d[f], x) for x in peers) * 2 > len(peers))
                    w.writerow([pid(c), s, f, int(present), int(VALIDATORS[f](d[f])) if present else "", agree])
    sums(pub)

    def dump(name, cursor):
        with (loc / name).open("w", encoding="utf-8") as fh:
            for d in cursor:
                fh.write(json.dumps(d, ensure_ascii=False, default=str) + "\n")
    dump("runs.jsonl", runs)
    dump("telemetry.jsonl", tel)
    dump("raw_responses.jsonl", db[st.RAW].find({"run_id": {"$in": run_ids}}, {"_id": 0}))
    dump("records.jsonl", db[st.RECORDS].find({"run_id": {"$in": run_ids}}, {"_id": 0}))
    sums(loc)
    print(pub)
    print(loc)

"""Step 20 — import the seed file (JSONL; format in docs/reproduce.md) into seed_companies.

Rejects CNPJs with invalid check digits, keeps only non-empty reference fields.
Usage: python scripts/20_import_seed.py [--file data/seed/seed_companies.jsonl] [--replace]
"""
import _bootstrap  # noqa: F401

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from pymongo import ReplaceOne

from cnpjbench import cnpj as cn
from cnpjbench import storage as st
from cnpjbench.config import get_settings
from cnpjbench.normalize import blank

REF_FIELDS = {"legal_name", "address_street", "address_number", "address_district", "address_city",
              "address_state", "address_zip", "address_city_ibge", "phones", "registered_at"}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=None)
    ap.add_argument("--replace", action="store_true", help="drop seed_companies before import")
    a = ap.parse_args()
    s = get_settings()
    path = s.resolve(Path(a.file) if a.file else s.seed_file)
    db = st.get_db()
    if a.replace:
        db[st.SEED].drop()
        st.ensure_indexes(db)

    stats, ops, now = Counter(), [], datetime.now(timezone.utc)
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            stats["lines"] += 1
            row = json.loads(line)
            c = cn.normalize(row.get("cnpj"))
            if not cn.is_valid(c):
                stats["rejected_invalid_cnpj"] += 1
                continue
            ref = {k: v for k, v in (row.get("ref") or {}).items() if k in REF_FIELDS and not blank(v)}
            ops.append(ReplaceOne({"_id": c}, {
                "_id": c, "cnpj": c, "ref": ref,
                "ref_duplicates": int(row.get("ref_duplicates") or 1),
                "is_head_office": cn.is_head_office(c), "is_alphanumeric": cn.is_alphanumeric(c),
                "imported_at": now}, upsert=True))
            stats["accepted"] += 1
    for i in range(0, len(ops), 2000):
        db[st.SEED].bulk_write(ops[i:i + 2000], ordered=False)
    stats["collection_total"] = db[st.SEED].count_documents({})
    print(json.dumps(dict(stats), indent=1))

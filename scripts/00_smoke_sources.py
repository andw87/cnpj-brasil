"""Step 00 — smoke test every implemented connector with a public CNPJ. Persists nothing.

Usage: python scripts/00_smoke_sources.py [--cnpj 33000167000101] [--status active] [--save]
"""
import _bootstrap  # noqa: F401

import argparse
import asyncio
import json

from cnpjbench.catalog import load_catalog
from cnpjbench.config import PROJECT_ROOT
from cnpjbench.connectors import REGISTRY, get_connector
from cnpjbench.runner import fetch_one, make_client
from cnpjbench.schema import SCORED_FIELDS


async def main(a):
    out_dir = PROJECT_ROOT / "data" / "smoke"
    async with make_client() as client:
        for src in load_catalog().values():
            if src.status != a.status or src.source_id not in REGISTRY:
                continue
            r = await fetch_one(client, get_connector(src.source_id), a.cnpj)
            t = r["telemetry"]
            filled = len([f for f in SCORED_FIELDS if f in (r["record"].to_doc() if r["record"] else {})])
            print(f"{src.source_id} {src.slug:24} {t['outcome']:13} http={t['http_status']} "
                  f"{t['latency_ms']:8.1f}ms fields={filled}/{len(SCORED_FIELDS)} {t.get('error', '')}")
            if a.save and r["payload"] is not None:
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / f"{src.source_id.lower()}_{a.cnpj}.json").write_text(
                    json.dumps(r["payload"], ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cnpj", default="33000167000101")
    ap.add_argument("--status", default="active")
    ap.add_argument("--save", action="store_true", help="write payloads to data/smoke/")
    asyncio.run(main(ap.parse_args()))

"""Step 10 — create collections and indexes (docs/reproduce.md). Idempotent.

Usage: python scripts/10_init_db.py
"""
import _bootstrap  # noqa: F401

from cnpjbench.storage import ensure_indexes, get_db

if __name__ == "__main__":
    db = get_db()
    db.command("ping")
    for coll, names in ensure_indexes(db).items():
        print(f"{coll:16} {', '.join(names)}")

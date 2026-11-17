"""Loads catalog/sources.yaml (docs/reproduce.md, adding a source). Source IDs are the telemetry key."""
from __future__ import annotations

import re
from functools import lru_cache

import yaml
from pydantic import BaseModel, field_validator

from .config import get_settings

SourceStatus = str  # active | pending_credentials | planned | rejected


class Source(BaseModel):
    source_id: str
    slug: str
    name: str
    url_template: str | None
    access: str
    open_source: bool
    upstream: str
    rate_limit_rpm: float | None
    rate_limit_basis: str | None
    status: SourceStatus
    probe_2026_11_16: str | None = None

    @field_validator("source_id")
    @classmethod
    def _id_shape(cls, v: str) -> str:
        if not re.fullmatch(r"S\d{2}", v):
            raise ValueError(f"source_id must match S\\d{{2}}: {v}")
        return v

    @property
    def connector_name(self) -> str:
        return f"{self.source_id.lower()}_{self.slug}"


@lru_cache
def load_catalog() -> dict[str, Source]:
    s = get_settings()
    raw = yaml.safe_load(s.resolve(s.catalog_file).read_text(encoding="utf-8"))
    sources = [Source(**item) for item in raw["sources"]]
    ids = [x.source_id for x in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate source_id in catalog")
    return {x.source_id: x for x in sources}


def get_source(source_id: str) -> Source:
    cat = load_catalog()
    sid = source_id.upper()
    if sid not in cat:
        raise KeyError(f"unknown source_id {source_id}")
    return cat[sid]

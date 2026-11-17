"""Connector contract (docs/reproduce.md, adding a source).

A connector is stateless: it builds the request for one CNPJ, classifies the response
into an outcome and maps a found payload to CanonicalCompany. Transport, pacing,
retries and telemetry belong to the runner, so every source is measured the same way.
"""
from __future__ import annotations

from typing import Any, ClassVar

import httpx

from ..catalog import Source, get_source
from ..schema import CanonicalCompany

# Outcome taxonomy (docs/methodology.md, section 5). Final outcomes end the CNPJ; retryable ones may be retried.
FOUND = "found"
NOT_FOUND = "not_found"
INVALID_INPUT = "invalid_input"
RATE_LIMITED = "rate_limited"
CLIENT_ERROR = "client_error"
SERVER_ERROR = "server_error"
TIMEOUT = "timeout"
NETWORK_ERROR = "network_error"
PARSE_ERROR = "parse_error"
RESTRICTED = "restricted"   # provider withholds the record on the free tier (paywall, cache-only)
RETRYABLE = frozenset({RATE_LIMITED, SERVER_ERROR, TIMEOUT, NETWORK_ERROR})

REGISTRY: dict[str, type["BaseConnector"]] = {}


class BaseConnector:
    source_id: ClassVar[str]
    # Top-level payload key holding the provider's own "record updated at" timestamp, if any (F3).
    declared_update_key: ClassVar[str | None] = None

    def __init_subclass__(cls, **kw: Any) -> None:
        super().__init_subclass__(**kw)
        REGISTRY[cls.source_id] = cls

    def __init__(self, source: Source | None = None):
        self.source = source or get_source(self.source_id)

    # -- request -----------------------------------------------------------------------
    formatted_cnpj: bool = False   # set by the runner: send 12.345.678/0001-95 (slash as %2F)

    def url(self, cnpj: str) -> str:
        assert self.source.url_template, f"{self.source_id} has no url_template"
        if self.formatted_cnpj:
            from ..cnpj import format_cnpj
            cnpj = format_cnpj(cnpj).replace("/", "%2F")
        return self.source.url_template.format(cnpj=cnpj)

    def headers(self) -> dict[str, str]:
        return {"Accept": "application/json"}

    # -- response ----------------------------------------------------------------------
    def classify(self, resp: httpx.Response, payload: Any) -> str:
        sc = resp.status_code
        if sc == 200:
            return FOUND
        if sc == 404:
            return NOT_FOUND
        if sc == 429:
            return RATE_LIMITED
        if sc in (400, 422):
            return INVALID_INPUT
        if sc >= 500:
            return SERVER_ERROR
        return CLIENT_ERROR

    def parse(self, cnpj: str, payload: Any) -> CanonicalCompany:
        raise NotImplementedError

"""S01 — BrasilAPI. Payload is the Minha Receita format."""
from __future__ import annotations

from ._formats import parse_minhareceita
from .base import BaseConnector


class S01BrasilApi(BaseConnector):
    source_id = "S01"

    def parse(self, cnpj, payload):
        return parse_minhareceita(cnpj, payload)

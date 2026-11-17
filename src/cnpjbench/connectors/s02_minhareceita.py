"""S02 — Minha Receita, public instance."""
from __future__ import annotations

from ._formats import parse_minhareceita
from .base import BaseConnector


class S02MinhaReceita(BaseConnector):
    source_id = "S02"

    def parse(self, cnpj, payload):
        return parse_minhareceita(cnpj, payload)

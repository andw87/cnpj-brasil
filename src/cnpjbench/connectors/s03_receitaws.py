"""S03 — ReceitaWS, free tier.

Errors come as HTTP 200 (or 404) with {"status": "ERROR", "message": ...}; "not in cache" = restricted.
Secondary CNAE "00.00-0-00" means "none" and is dropped.
"""
from __future__ import annotations

import re

from .. import normalize as n
from ..schema import CanonicalCompany, Partner
from .base import CLIENT_ERROR, FOUND, INVALID_INPUT, NOT_FOUND, RESTRICTED, BaseConnector


class S03ReceitaWs(BaseConnector):
    source_id = "S03"
    declared_update_key = "ultima_atualizacao"

    def classify(self, resp, payload):
        out = super().classify(resp, payload)
        if isinstance(payload, dict) and payload.get("status") == "ERROR" and "CACHE" in n.fold(payload.get("message")):
            return RESTRICTED          # free API serves its cache only ("not in cache")
        if out != FOUND:
            return out
        if isinstance(payload, dict) and payload.get("status") == "ERROR":
            msg = n.fold(payload.get("message"))
            if "INVALIDO" in msg:
                return INVALID_INPUT
            if "NAO ENCONTRADO" in msg or "NAO EXISTE" in msg or "REJEITADO" in msg:
                return NOT_FOUND
            return CLIENT_ERROR
        return FOUND

    def parse(self, cnpj, p):
        nat = n.text(p.get("natureza_juridica")) or ""
        m = re.match(r"^(\d{3}-?\d)\s*-\s*(.+)$", nat)
        main = (p.get("atividade_principal") or [{}])[0]
        return CanonicalCompany(
            cnpj=cnpj,
            legal_name=n.text(p.get("nome")),
            trade_name=n.text(p.get("fantasia")),
            establishment_type={"MATRIZ": "head_office", "FILIAL": "branch"}.get(n.fold(p.get("tipo"))),
            registration_status=n.status(p.get("situacao")),
            registration_status_date=n.iso_date(p.get("data_situacao")),
            opening_date=n.iso_date(p.get("abertura")),
            legal_nature_code=n.code(m.group(1), 4) if m else None,
            legal_nature=n.text(m.group(2)) if m else n.text(nat),
            company_size=n.text(p.get("porte")),
            share_capital=n.money(p.get("capital_social")),
            main_cnae=n.code(main.get("code"), 7),
            secondary_cnaes=[c for c in (n.code(x.get("code"), 7) for x in p.get("atividades_secundarias") or []) if c],
            address_street=n.text(p.get("logradouro")),
            address_number=n.text(p.get("numero")),
            address_complement=n.text(p.get("complemento")),
            address_district=n.text(p.get("bairro")),
            address_city=n.text(p.get("municipio")),
            address_state=n.text(p.get("uf")),
            address_zip=n.digits(p.get("cep")),
            phones=n.phones([p.get("telefone")]),
            email=n.text(p.get("email")),
            partners=[Partner(name=s["nome"], role=n.strip_role_code(s.get("qual")))
                      for s in p.get("qsa") or [] if n.text(s.get("nome"))],
            simples_optant=(p.get("simples") or {}).get("optante"),
            mei_optant=(p.get("simei") or {}).get("optante"),
            source_updated_at=n.iso_datetime(p.get("ultima_atualizacao")),
        )

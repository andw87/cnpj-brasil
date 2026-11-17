"""S07 — OpenCNPJ.com (kitana.opencnpj.com).

Envelope {"success": bool, "data": {...}}. The first element of data.cnaes is the main CNAE.
Legal nature comes as "Text (code)".
"""
from __future__ import annotations

import re

from .. import normalize as n
from ..schema import CanonicalCompany, Partner
from .base import FOUND, NOT_FOUND, BaseConnector


class S07OpenCnpjCom(BaseConnector):
    source_id = "S07"

    def classify(self, resp, payload):
        out = super().classify(resp, payload)
        if out == FOUND and isinstance(payload, dict) and not (payload.get("success") and payload.get("data")):
            return NOT_FOUND
        return out

    def parse(self, cnpj, payload):
        p = payload.get("data") or {}
        nat = n.text(p.get("naturezaJuridica")) or ""
        m = re.match(r"^(.*)\((\d{3,4})\)\s*$", nat)
        cnaes = [c for c in (n.code(x.get("cnae"), 7) for x in p.get("cnaes") or []) if c]
        matriz = n.yes_no(p.get("matriz"))
        return CanonicalCompany(
            cnpj=cnpj,
            legal_name=n.text(p.get("razaoSocial")),
            trade_name=n.text(p.get("nomeFantasia")),
            establishment_type=None if matriz is None else ("head_office" if matriz else "branch"),
            registration_status=n.status(p.get("situacaoCadastral")),
            registration_status_date=n.iso_date(p.get("dataSituacaoCadastral")),
            opening_date=n.iso_date(p.get("dataInicioAtividades")),
            legal_nature_code=n.code(m.group(2), 4) if m else None,
            legal_nature=n.text(m.group(1)) if m else n.text(nat),
            share_capital=n.money(p.get("capitalSocial")),
            main_cnae=cnaes[0] if cnaes else None,
            secondary_cnaes=cnaes[1:],
            address_street=n.text(p.get("logradouro")),
            address_number=n.text(p.get("numero")),
            address_complement=n.text(p.get("complemento")),
            address_district=n.text(p.get("bairro")),
            address_city=n.text(p.get("municipio")),
            address_state=n.text(p.get("uf")),
            address_zip=n.digits(p.get("cep")),
            phones=n.phones([p.get("telefone")]),
            email=n.text(p.get("email")),
            partners=[Partner(name=s["nomeSocio"], role=n.text(s.get("descricao")))
                      for s in p.get("socios") or [] if n.text(s.get("nomeSocio"))],
            simples_optant=n.yes_no(p.get("opcaoSimples")),
            mei_optant=n.yes_no(p.get("opcaoMei")),
        )

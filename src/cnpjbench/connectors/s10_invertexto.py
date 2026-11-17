"""S10 — Invertexto (free token). Status pending_credentials: mapping is written
against the public documentation and must be confirmed with a real payload before activation."""
from __future__ import annotations

from .. import normalize as n
from ..config import get_settings
from ..schema import CanonicalCompany, Partner
from .base import BaseConnector


class S10Invertexto(BaseConnector):
    source_id = "S10"

    def url(self, cnpj):
        return self.source.url_template.format(cnpj=cnpj, token=get_settings().s10_token)

    def parse(self, cnpj, p):
        end = p.get("endereco") or {}
        ativ = p.get("atividade_principal") or {}
        return CanonicalCompany(
            cnpj=cnpj,
            legal_name=n.text(p.get("razao_social")),
            trade_name=n.text(p.get("nome_fantasia")),
            establishment_type={"MATRIZ": "head_office", "FILIAL": "branch"}.get(n.fold(p.get("tipo"))),
            registration_status=n.status(p.get("situacao", {}).get("nome") if isinstance(p.get("situacao"), dict) else p.get("situacao")),
            opening_date=n.iso_date(p.get("data_inicio")),
            legal_nature=n.text(p.get("natureza_juridica")),
            company_size=n.text(p.get("porte")),
            share_capital=n.money(p.get("capital_social")),
            main_cnae=n.code(ativ.get("codigo"), 7),
            address_street=n.join(end.get("tipo_logradouro"), end.get("logradouro")),
            address_number=n.text(end.get("numero")),
            address_complement=n.text(end.get("complemento")),
            address_district=n.text(end.get("bairro")),
            address_city=n.text(end.get("municipio")),
            address_state=n.text(end.get("uf")),
            address_zip=n.digits(end.get("cep")),
            phones=n.phones([p.get("telefone1"), p.get("telefone2")]),
            email=n.text(p.get("email")),
            partners=[Partner(name=s["nome"], role=n.text(s.get("qualificacao")))
                      for s in p.get("socios") or [] if n.text(s.get("nome"))],
        )

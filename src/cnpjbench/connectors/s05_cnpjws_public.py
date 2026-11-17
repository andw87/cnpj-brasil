"""S05 — CNPJ.ws public API (publica.cnpj.ws)."""
from __future__ import annotations

from .. import normalize as n
from ..schema import CanonicalCompany, Partner
from .base import BaseConnector


class S05CnpjWsPublic(BaseConnector):
    source_id = "S05"
    declared_update_key = "atualizado_em"

    def parse(self, cnpj, p):
        e = p.get("estabelecimento") or {}
        simples = p.get("simples") or {}
        return CanonicalCompany(
            cnpj=cnpj,
            legal_name=n.text(p.get("razao_social")),
            trade_name=n.text(e.get("nome_fantasia")),
            establishment_type={"MATRIZ": "head_office", "FILIAL": "branch"}.get(n.fold(e.get("tipo"))),
            registration_status=n.status(e.get("situacao_cadastral")),
            registration_status_date=n.iso_date(e.get("data_situacao_cadastral")),
            opening_date=n.iso_date(e.get("data_inicio_atividade")),
            legal_nature_code=n.code((p.get("natureza_juridica") or {}).get("id"), 4),
            legal_nature=n.text((p.get("natureza_juridica") or {}).get("descricao")),
            company_size=n.text((p.get("porte") or {}).get("descricao")),
            share_capital=n.money(p.get("capital_social")),
            main_cnae=n.code((e.get("atividade_principal") or {}).get("id"), 7),
            secondary_cnaes=[c for c in (n.code(x.get("id"), 7) for x in e.get("atividades_secundarias") or []) if c],
            address_street=n.join(e.get("tipo_logradouro"), e.get("logradouro")),
            address_number=n.text(e.get("numero")),
            address_complement=n.text(e.get("complemento")),
            address_district=n.text(e.get("bairro")),
            address_city=n.text((e.get("cidade") or {}).get("nome")),
            address_state=n.text((e.get("estado") or {}).get("sigla")),
            address_zip=n.digits(e.get("cep")),
            address_city_ibge=n.code((e.get("cidade") or {}).get("ibge_id"), 7),
            phones=n.phones([f"{e.get('ddd1') or ''}{e.get('telefone1') or ''}",
                             f"{e.get('ddd2') or ''}{e.get('telefone2') or ''}"]),
            email=n.text(e.get("email")),
            partners=[Partner(name=s["nome"], role=n.text((s.get("qualificacao_socio") or {}).get("descricao")))
                      for s in p.get("socios") or [] if n.text(s.get("nome"))],
            simples_optant=n.yes_no(simples.get("simples")) if simples else None,
            mei_optant=n.yes_no(simples.get("mei")) if simples else None,
            source_updated_at=n.iso_datetime(e.get("atualizado_em") or p.get("atualizado_em")),
        )

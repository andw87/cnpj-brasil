"""S06 — OpenCNPJ (api.opencnpj.org). Fax numbers are excluded from phones."""
from __future__ import annotations

from .. import normalize as n
from ..schema import CanonicalCompany, Partner
from .base import BaseConnector


class S06OpenCnpjOrg(BaseConnector):
    source_id = "S06"
    declared_update_key = "updated_at"

    def parse(self, cnpj, p):
        return CanonicalCompany(
            cnpj=cnpj,
            legal_name=n.text(p.get("razao_social")),
            trade_name=n.text(p.get("nome_fantasia")),
            establishment_type={"MATRIZ": "head_office", "FILIAL": "branch"}.get(n.fold(p.get("matriz_filial"))),
            registration_status=n.status(p.get("situacao_cadastral")),
            registration_status_date=n.iso_date(p.get("data_situacao_cadastral")),
            opening_date=n.iso_date(p.get("data_inicio_atividade")),
            legal_nature_code=n.code(p.get("codigo_natureza_juridica"), 4),
            legal_nature=n.text(p.get("natureza_juridica")),
            company_size=n.text(p.get("porte_empresa")),
            share_capital=n.money(p.get("capital_social")),
            main_cnae=n.code(p.get("cnae_principal"), 7),
            secondary_cnaes=[c for c in (n.code(x, 7) for x in p.get("cnaes_secundarios") or []) if c],
            address_street=n.join(p.get("tipo_logradouro"), p.get("logradouro")),
            address_number=n.text(p.get("numero")),
            address_complement=n.text(p.get("complemento")),
            address_district=n.text(p.get("bairro")),
            address_city=n.text(p.get("municipio")),
            address_state=n.text(p.get("uf")),
            address_zip=n.digits(p.get("cep")),
            phones=n.phones([f"{t.get('ddd', '')}{t.get('numero', '')}"
                             for t in p.get("telefones") or [] if not t.get("is_fax")]),
            email=n.text(p.get("email")),
            partners=[Partner(name=s["nome_socio"], role=n.text(s.get("qualificacao_socio")))
                      for s in p.get("QSA") or [] if n.text(s.get("nome_socio"))],
            simples_optant=n.yes_no(p.get("opcao_simples")),
            mei_optant=n.yes_no(p.get("opcao_mei")),
            source_updated_at=n.iso_datetime(p.get("updated_at")),
        )

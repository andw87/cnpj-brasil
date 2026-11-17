"""Payload formats shared by more than one source."""
from __future__ import annotations

from typing import Any

from .. import normalize as n
from ..schema import CanonicalCompany, Partner


def parse_minhareceita(cnpj: str, p: dict[str, Any]) -> CanonicalCompany:
    """Minha Receita JSON (also served by BrasilAPI)."""
    mf = p.get("identificador_matriz_filial")
    return CanonicalCompany(
        cnpj=cnpj,
        legal_name=n.text(p.get("razao_social")),
        trade_name=n.text(p.get("nome_fantasia")),
        establishment_type={1: "head_office", 2: "branch"}.get(mf),
        registration_status=n.status(p.get("situacao_cadastral")),
        registration_status_date=n.iso_date(p.get("data_situacao_cadastral")),
        opening_date=n.iso_date(p.get("data_inicio_atividade")),
        legal_nature_code=n.code(p.get("codigo_natureza_juridica"), 4),
        legal_nature=n.text(p.get("natureza_juridica")),
        company_size=n.text(p.get("porte")),
        share_capital=n.money(p.get("capital_social")),
        main_cnae=n.code(p.get("cnae_fiscal"), 7),
        secondary_cnaes=[c for c in (n.code(x.get("codigo"), 7) for x in p.get("cnaes_secundarios") or []) if c],
        address_street=n.join(p.get("descricao_tipo_de_logradouro"), p.get("logradouro")),
        address_number=n.text(p.get("numero")),
        address_complement=n.text(p.get("complemento")),
        address_district=n.text(p.get("bairro")),
        address_city=n.text(p.get("municipio")),
        address_state=n.text(p.get("uf")),
        address_zip=n.digits(p.get("cep")),
        address_city_ibge=n.code(p.get("codigo_municipio_ibge"), 7),
        phones=n.phones([p.get("ddd_telefone_1"), p.get("ddd_telefone_2")]),
        email=n.text(p.get("email")),
        partners=[Partner(name=s["nome_socio"], role=n.text(s.get("qualificacao_socio")))
                  for s in p.get("qsa") or [] if n.text(s.get("nome_socio"))],
        simples_optant=p.get("opcao_pelo_simples"),
        mei_optant=p.get("opcao_pelo_mei"),
    )

"""S04 — CNPJa Open (open.cnpja.com)."""
from __future__ import annotations

from .. import normalize as n
from ..schema import CanonicalCompany, Partner
from .base import RESTRICTED, BaseConnector


class S04CnpjaOpen(BaseConnector):
    source_id = "S04"
    declared_update_key = "updated"

    def classify(self, resp, payload):
        if resp.status_code == 402:    # "recently founded offices only available in commercial api"
            return RESTRICTED
        return super().classify(resp, payload)

    def parse(self, cnpj, p):
        co = p.get("company") or {}
        addr = p.get("address") or {}
        head = p.get("head")
        emails = [e.get("address") for e in p.get("emails") or [] if e.get("address")]
        return CanonicalCompany(
            cnpj=cnpj,
            legal_name=n.text(co.get("name")),
            trade_name=n.text(p.get("alias")),
            establishment_type=None if head is None else ("head_office" if head else "branch"),
            registration_status=n.status((p.get("status") or {}).get("id")),
            registration_status_date=n.iso_date(p.get("statusDate")),
            opening_date=n.iso_date(p.get("founded")),
            legal_nature_code=n.code((co.get("nature") or {}).get("id"), 4),
            legal_nature=n.text((co.get("nature") or {}).get("text")),
            company_size=n.text((co.get("size") or {}).get("acronym")),
            share_capital=n.money(co.get("equity")),
            main_cnae=n.code((p.get("mainActivity") or {}).get("id"), 7),
            secondary_cnaes=[c for c in (n.code(x.get("id"), 7) for x in p.get("sideActivities") or []) if c],
            address_street=n.text(addr.get("street")),
            address_number=n.text(addr.get("number")),
            address_complement=n.text(addr.get("details")),
            address_district=n.text(addr.get("district")),
            address_city=n.text(addr.get("city")),
            address_state=n.text(addr.get("state")),
            address_zip=n.digits(addr.get("zip")),
            address_city_ibge=n.code(addr.get("municipality"), 7),
            phones=n.phones([f"{ph.get('area', '')}{ph.get('number', '')}" for ph in p.get("phones") or []]),
            email=emails[0] if emails else None,
            partners=[Partner(name=m["person"]["name"], role=n.text((m.get("role") or {}).get("text")))
                      for m in co.get("members") or [] if n.text((m.get("person") or {}).get("name"))],
            simples_optant=(co.get("simples") or {}).get("optant"),
            mei_optant=(co.get("simei") or {}).get("optant"),
            source_updated_at=n.iso_datetime(p.get("updated")),
        )

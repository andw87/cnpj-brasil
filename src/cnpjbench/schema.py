"""Canonical company record (docs/methodology.md, section 6). Every connector maps its payload to this model."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

RegistrationStatus = Literal["active", "suspended", "unfit", "closed", "null"]
EstablishmentType = Literal["head_office", "branch"]


class Partner(BaseModel):
    name: str
    role: str | None = None


class CanonicalCompany(BaseModel):
    cnpj: str
    legal_name: str | None = None
    trade_name: str | None = None
    establishment_type: EstablishmentType | None = None
    registration_status: RegistrationStatus | None = None
    registration_status_date: str | None = None
    opening_date: str | None = None
    legal_nature_code: str | None = None
    legal_nature: str | None = None
    company_size: str | None = None
    share_capital: float | None = None
    main_cnae: str | None = None
    secondary_cnaes: list[str] = []
    address_street: str | None = None
    address_number: str | None = None
    address_complement: str | None = None
    address_district: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_zip: str | None = None
    address_city_ibge: str | None = None
    phones: list[str] = []
    email: str | None = None
    partners: list[Partner] = []
    simples_optant: bool | None = None
    mei_optant: bool | None = None
    source_updated_at: str | None = None

    def to_doc(self) -> dict:
        """Sparse document: empty values are not persisted (docs/reproduce.md)."""
        return {k: v for k, v in self.model_dump(mode="json").items() if v not in (None, [], "")}


# Fields evaluated by completeness / validity / agreement metrics (docs/methodology.md, section 5).
# source_updated_at is metadata, not company data, so it is excluded.
SCORED_FIELDS: tuple[str, ...] = tuple(
    f for f in CanonicalCompany.model_fields if f not in ("cnpj", "source_updated_at")
)

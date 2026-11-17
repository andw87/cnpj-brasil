"""Every active connector must map the same public company (Petrobras head office) to the
same canonical core values. Fixtures are real payloads captured on 2026-11-16."""
import json
from pathlib import Path

import httpx
import pytest

from cnpjbench.connectors import get_connector
from cnpjbench.connectors.base import FOUND, INVALID_INPUT, NOT_FOUND
from cnpjbench.metrics import VALIDATORS

FIX = Path(__file__).parent / "fixtures"
CNPJ = "33000167000101"
ACTIVE = ["S01", "S02", "S03", "S04", "S05", "S06", "S07"]


def load(sid):
    return json.loads((FIX / f"{sid.lower()}_{CNPJ}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("sid", ACTIVE)
def test_core_fields(sid):
    conn = get_connector(sid)
    payload = load(sid)
    assert conn.classify(httpx.Response(200), payload) == FOUND
    r = conn.parse(CNPJ, payload)
    assert r.legal_name == "PETROLEO BRASILEIRO S A PETROBRAS"
    assert r.establishment_type == "head_office"
    assert r.registration_status == "active"
    assert r.registration_status_date == "2005-11-03"
    assert r.opening_date == "1966-09-28"
    assert r.main_cnae == "0600001"
    assert r.address_state == "RJ"
    assert r.address_zip == "20031170"
    assert r.address_number == "65"
    assert r.partners, "partners expected"


@pytest.mark.parametrize("sid", ACTIVE)
def test_values_pass_validators(sid):
    doc = get_connector(sid).parse(CNPJ, load(sid)).to_doc()
    bad = [f for f, v in doc.items() if f in VALIDATORS and not VALIDATORS[f](v)]
    assert not bad, bad


def test_sparse_document_omits_empty():
    doc = get_connector("S01").parse(CNPJ, load("S01")).to_doc()
    assert "address_complement" not in doc and "email" not in doc


def test_receitaws_error_in_200():
    conn = get_connector("S03")
    assert conn.classify(httpx.Response(200), {"status": "ERROR", "message": "CNPJ inválido"}) == INVALID_INPUT


def test_kitana_envelope_not_found():
    conn = get_connector("S07")
    assert conn.classify(httpx.Response(200), {"success": False, "data": None}) == NOT_FOUND

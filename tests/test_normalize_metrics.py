from cnpjbench import normalize as n
from cnpjbench.metrics import same, similar


def test_money_formats():
    assert n.money("205431960490,52") == 205431960490.52
    assert n.money("1.234,50") == 1234.5
    assert n.money("205431960490.52") == 205431960490.52
    assert n.money(10) == 10.0


def test_dates_and_status():
    assert n.iso_date("28/09/1966") == "1966-09-28"
    assert n.iso_date("1966-09-28") == "1966-09-28"
    assert n.iso_date("") is None
    assert n.status(2) == "active" and n.status("Baixada") == "closed"


def test_phones_split_and_dedup():
    assert n.phones(["(21) 2166-0000 / (21) 2166-0000", "21 3224-1111"]) == ["2121660000", "2132241111"]


def test_agreement_rules():
    assert same("legal_name", "PETROLEO BRASILEIRO S A PETROBRAS", "Petróleo Brasileiro S.A. - Petrobras")
    assert same("address_city", "SÃO PAULO", "Sao Paulo")
    assert not same("share_capital", 205431960000, 205431960490.52)
    assert same("phones", ["2121660000"], ["2121660000"])
    assert similar("ABC", "ABC") == 1.0


def test_company_size_labels_compare_by_code():
    from cnpjbench.metrics import same
    assert same("company_size", "ME", "Microempresa (ME)")
    assert same("company_size", "EMPRESA DE PEQUENO PORTE", "EPP")
    assert not same("company_size", "ME", "DEMAIS")


def test_wilson_interval():
    from cnpjbench.metrics import wilson
    lo, hi = wilson(297, 300)
    assert 0.97 < lo < 0.99 and hi > 0.995
    assert wilson(0, 0) is None


def test_head_office_cnpj_check_digits():
    from cnpjbench.cnpj import head_office_cnpj, is_valid
    assert head_office_cnpj("33000167") == "33000167000101"
    assert is_valid(head_office_cnpj("12ABC345"))

from cnpjbench import cnpj as cn


def test_numeric_valid():
    assert cn.is_valid("33.000.167/0001-01")
    assert cn.is_valid("00000000000191")


def test_alphanumeric_valid():
    # official example published by Receita Federal for the 2026 alphanumeric CNPJ
    assert cn.is_valid("12.ABC.345/01DE-35")
    assert cn.is_alphanumeric("12ABC34501DE35")


def test_invalid():
    assert not cn.is_valid("33000167000102")
    assert not cn.is_valid("11111111111111")
    assert not cn.is_valid("123")
    assert not cn.is_valid(None)


def test_head_office_and_format():
    assert cn.is_head_office("33000167000101")
    assert not cn.is_head_office("33000167000292")
    assert cn.format_cnpj("33000167000101") == "33.000.167/0001-01"

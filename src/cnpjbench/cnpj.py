"""CNPJ normalization and check-digit validation.

Supports the numeric format and the alphanumeric format issued by Receita Federal
since July 2026 (12 alphanumeric base characters + 2 numeric check digits).
Character value = ord(char) - 48, so digits keep their value and 'A' = 17 ... 'Z' = 42.
"""
from __future__ import annotations

import re

_WEIGHTS_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_WEIGHTS_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_SHAPE = re.compile(r"^[0-9A-Z]{12}[0-9]{2}$")


def normalize(value: str | None) -> str:
    """Uppercase and strip every character that is not 0-9 or A-Z."""
    return re.sub(r"[^0-9A-Z]", "", (value or "").upper())


def _check_digit(base: str, weights: list[int]) -> int:
    total = sum((ord(c) - 48) * w for c, w in zip(base, weights))
    rest = total % 11
    return 0 if rest < 2 else 11 - rest


def is_valid(value: str | None) -> bool:
    c = normalize(value)
    if not _SHAPE.match(c) or len(set(c)) == 1:
        return False
    d1 = _check_digit(c[:12], _WEIGHTS_1)
    d2 = _check_digit(c[:12] + str(d1), _WEIGHTS_2)
    return c[12:] == f"{d1}{d2}"


def is_alphanumeric(value: str | None) -> bool:
    return any(ch.isalpha() for ch in normalize(value))


def is_head_office(value: str | None) -> bool:
    """Order segment 0001 identifies the head office (matriz)."""
    return normalize(value)[8:12] == "0001"


def head_office_cnpj(base: str) -> str:
    """Full head-office CNPJ (order 0001) with check digits for an 8-character base."""
    b = normalize(base) + "0001"
    d1 = _check_digit(b, _WEIGHTS_1)
    d2 = _check_digit(b + str(d1), _WEIGHTS_2)
    return f"{b}{d1}{d2}"


def format_cnpj(value: str | None) -> str:
    c = normalize(value)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}" if len(c) == 14 else c

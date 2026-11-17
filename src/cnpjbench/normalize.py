"""Value normalizers shared by every connector (docs/methodology.md, section 6)."""
from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from typing import Any, Iterable

# Receita Federal "situacao cadastral" codes and texts -> canonical enum
_STATUS_BY_CODE = {1: "null", 2: "active", 3: "suspended", 4: "unfit", 8: "closed"}
_STATUS_BY_TEXT = {
    "NULA": "null", "ATIVA": "active", "SUSPENSA": "suspended",
    "INAPTA": "unfit", "BAIXADA": "closed",
}


def blank(v: Any) -> bool:
    return v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict)) and not v)


def text(v: Any) -> str | None:
    """Trimmed string with collapsed whitespace, or None when empty."""
    if blank(v):
        return None
    s = re.sub(r"\s+", " ", str(v)).strip()
    return s or None


def digits(v: Any) -> str | None:
    if v is None:
        return None
    s = re.sub(r"\D", "", str(v))
    return s or None


def code(v: Any, width: int) -> str | None:
    """Numeric code as zero-padded string (CNAE=7, legal nature=4, IBGE=7)."""
    d = digits(v)
    return d.zfill(width) if d and int(d) != 0 else None


def iso_date(v: Any) -> str | None:
    """Accepts YYYY-MM-DD, DD/MM/YYYY or ISO datetime; returns YYYY-MM-DD."""
    s = text(v)
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s[:10], fmt).date().isoformat()
        except ValueError:
            continue
    return None


def iso_datetime(v: Any) -> str | None:
    s = text(v)
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")[:26]).isoformat()
    except ValueError:
        return iso_date(s)


def money(v: Any) -> float | None:
    """Accepts numbers, '1234.56' and '1.234,56'."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def status(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, int) or (isinstance(v, str) and v.strip().isdigit()):
        return _STATUS_BY_CODE.get(int(v))
    return _STATUS_BY_TEXT.get(fold(v))


def yes_no(v: Any) -> bool | None:
    if isinstance(v, bool):
        return v
    s = fold(v)
    if s in ("S", "SIM", "TRUE", "1"):
        return True
    if s in ("N", "NAO", "FALSE", "0"):
        return False
    return None


def fold(v: Any) -> str:
    """Uppercase, accent-free, single-spaced — used for comparisons, never stored."""
    if v is None:
        return ""
    s = unicodedata.normalize("NFKD", str(v))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", s).strip().upper()


def join(*parts: Any) -> str | None:
    return text(" ".join(p for p in (text(x) for x in parts) if p))


def phones(values: Iterable[Any]) -> list[str]:
    """Digits-only phones with area code (10-11 digits), deduplicated, order kept."""
    out: list[str] = []
    for v in values:
        for piece in re.split(r"[/;,]", str(v or "")):
            d = digits(piece)
            if d and d not in out:
                out.append(d)
    return out


def strip_role_code(v: Any) -> str | None:
    """'16-Presidente' -> 'Presidente'."""
    s = text(v)
    return re.sub(r"^\d+\s*-\s*", "", s) if s else None


def today() -> date:
    return date.today()

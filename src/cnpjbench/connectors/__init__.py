"""Connector registry. Importing this package registers every sNN_<slug> module."""
from __future__ import annotations

import importlib
import pkgutil

from .base import REGISTRY, BaseConnector

for _m in pkgutil.iter_modules(__path__):
    if _m.name[:1] == "s" and _m.name[1:3].isdigit():
        importlib.import_module(f"{__name__}.{_m.name}")


def get_connector(source_id: str) -> BaseConnector:
    sid = source_id.upper()
    if sid not in REGISTRY:
        raise KeyError(f"no connector implemented for {sid}")
    return REGISTRY[sid]()


__all__ = ["REGISTRY", "BaseConnector", "get_connector"]

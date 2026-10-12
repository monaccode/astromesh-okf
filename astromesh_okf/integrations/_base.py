"""Shared helpers for the framework adapters."""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Optional

from astromesh_okf.tools import Param


def require(module: str, extra: str) -> ModuleType:
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        raise ImportError(
            f"{module} is not installed. Install it with: pip install 'astromesh-okf[{extra}]'"
        ) from exc


def py_type(p: Param):
    base = {"string": str, "array": list[str], "boolean": bool, "integer": int}[p.type]
    return base if p.required or p.default is not None else Optional[base]  # noqa: UP045

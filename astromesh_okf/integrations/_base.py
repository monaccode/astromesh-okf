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
        msg = f"{module} is not installed. Install it with: pip install 'astromesh-okf[{extra}]'"
        if extra == "pydantic-ai":
            msg += " (requires Python >= 3.11)"
        raise ImportError(msg) from exc


def py_type(p: Param):
    base = {"string": str, "array": list[str], "boolean": bool, "integer": int}[p.type]
    return base if p.required or p.default is not None else Optional[base]  # noqa: UP045

"""PydanticAI Tools for an OKF bundle."""

from __future__ import annotations

from astromesh_okf.integrations._base import require
from astromesh_okf.tools import DESCRIPTIONS, OKFTools


def okf_tools(bundle, prefix: str = "") -> list:
    pai = require("pydantic_ai", "pydantic-ai")
    return [
        pai.Tool(fn, name=fn.__name__, description=DESCRIPTIONS[fn.okf_name])
        for fn in OKFTools(bundle, prefix).functions()
    ]

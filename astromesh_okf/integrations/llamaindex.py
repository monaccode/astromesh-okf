"""LlamaIndex FunctionTools for an OKF bundle."""

from __future__ import annotations

from astromesh_okf.integrations._base import require
from astromesh_okf.tools import DESCRIPTIONS, OKFTools


def okf_tools(bundle, prefix: str = "") -> list:
    li = require("llama_index.core.tools", "llamaindex")
    return [
        li.FunctionTool.from_defaults(
            fn=fn, name=fn.__name__, description=DESCRIPTIONS[fn.okf_name]
        )
        for fn in OKFTools(bundle, prefix).functions()
    ]

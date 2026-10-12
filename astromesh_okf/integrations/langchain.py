"""LangChain tools for an OKF bundle. LangGraph uses them as-is (create_react_agent, ToolNode)."""

from __future__ import annotations

from astromesh_okf.integrations._base import require
from astromesh_okf.tools import DESCRIPTIONS, OKFTools


def okf_tools(bundle, prefix: str = "") -> list:
    lc = require("langchain_core.tools", "langchain")
    return [
        lc.StructuredTool.from_function(
            func=fn, name=fn.__name__, description=DESCRIPTIONS[fn.okf_name]
        )
        for fn in OKFTools(bundle, prefix).functions()
    ]

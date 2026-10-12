"""LangChain tools for an OKF bundle.

Use them with `langchain.agents.create_agent` (LangGraph runtime underneath) or in a
LangGraph `ToolNode` as-is.
"""

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

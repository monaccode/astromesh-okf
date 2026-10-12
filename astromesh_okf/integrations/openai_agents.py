"""OpenAI Agents SDK function tools for an OKF bundle."""

from __future__ import annotations

from astromesh_okf.integrations._base import require
from astromesh_okf.tools import DESCRIPTIONS, OKFTools


def okf_tools(bundle, prefix: str = "") -> list:
    agents = require("agents", "openai-agents")
    return [
        agents.function_tool(
            fn, name_override=fn.__name__, description_override=DESCRIPTIONS[fn.okf_name]
        )
        for fn in OKFTools(bundle, prefix).functions()
    ]

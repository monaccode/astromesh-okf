"""Google ADK FunctionTools for an OKF bundle."""

from __future__ import annotations

from astromesh_okf.integrations._base import require
from astromesh_okf.tools import OKFTools


def okf_tools(bundle, prefix: str = "") -> list:
    adk = require("google.adk.tools", "adk")
    # ADK takes the tool name from __name__ and the description from the docstring.
    return [adk.FunctionTool(fn) for fn in OKFTools(bundle, prefix).functions()]

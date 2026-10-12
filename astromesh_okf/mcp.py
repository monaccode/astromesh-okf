"""Expose an OKF bundle's three tools over the Model Context Protocol (stdio by default)."""

from __future__ import annotations

from astromesh_okf.integrations._base import require
from astromesh_okf.tools import DESCRIPTIONS, OKFTools


def build_server(bundle, prefix: str = "", name: str = "astromesh-okf"):
    fastmcp = require("mcp.server.fastmcp", "mcp")
    server = fastmcp.FastMCP(name)
    for fn in OKFTools(bundle, prefix).functions():
        server.add_tool(fn, name=fn.__name__, description=DESCRIPTIONS[fn.okf_name])
    return server

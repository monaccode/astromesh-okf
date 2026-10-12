import asyncio
import json
from pathlib import Path

import pytest

pytest.importorskip("mcp")

from mcp.shared.memory import create_connected_server_and_client_session

from astromesh_okf.mcp import build_server

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "okf"


def test_lists_and_calls_tools_over_mcp():
    server = build_server(FIX, prefix="acme_")

    async def go():
        async with create_connected_server_and_client_session(server._mcp_server) as client:
            names = [t.name for t in (await client.list_tools()).tools]
            res = await client.call_tool("acme_kb_read", {"concept_id": "metrics/revenue"})
            return names, res.content[0].text

    names, text = asyncio.run(go())
    assert names == ["acme_kb_index", "acme_kb_read", "acme_kb_find"]
    assert json.loads(text)["title"] == "Revenue"

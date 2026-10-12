import asyncio
import json
from pathlib import Path

import pytest

pytest.importorskip("agents")

from astromesh_okf.integrations.openai_agents import okf_tools

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "okf"
ARGS = {"text", "type", "tags", "include_deprecated", "limit"}


def _call(t, **kw):
    from agents.tool_context import ToolContext

    raw = json.dumps(kw)
    ctx = ToolContext(context=None, tool_name=t.name, tool_call_id="c1", tool_arguments=raw)
    return asyncio.run(t.on_invoke_tool(ctx, raw))


def test_tools_names_and_schema():
    tools = okf_tools(FIX)
    assert [t.name for t in tools] == ["kb_index", "kb_read", "kb_find"]
    assert set(tools[2].params_json_schema["properties"]) == ARGS


def test_invoke_with_a_single_argument():
    _, read, find = okf_tools(FIX)
    out = json.loads(_call(find, type="Metric"))
    assert out["results"][0]["id"] == "metrics/churn"
    assert json.loads(_call(read, concept_id="metrics/revenue"))["title"] == "Revenue"


def test_prefix():
    assert next(t.name for t in okf_tools(FIX, prefix="acme_")) == "acme_kb_index"

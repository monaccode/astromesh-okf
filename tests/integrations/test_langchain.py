import json
from pathlib import Path

import pytest

pytest.importorskip("langchain_core")

from astromesh_okf.integrations.langchain import okf_tools

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "okf"


def test_tools_names_and_schema():
    tools = okf_tools(FIX)
    assert [t.name for t in tools] == ["kb_index", "kb_read", "kb_find"]
    t = tools[2]
    assert set(t.args) == {"text", "type", "tags", "include_deprecated", "limit"}


def test_invoke_with_a_single_argument():
    find = okf_tools(FIX)[2]
    out = json.loads(find.invoke({"type": "Metric"}))
    assert out["results"][0]["id"] == "metrics/churn"
    t = okf_tools(FIX)[1]
    assert json.loads(t.invoke({"concept_id": "metrics/revenue"}))["title"] == "Revenue"


def test_prefix():
    assert next(t.name for t in okf_tools(FIX, prefix="acme_")) == "acme_kb_index"

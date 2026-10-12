"""OKFTools: string results, errors as JSON, argument coercion, prefixes."""

import inspect
import json
import sys
from pathlib import Path

from astromesh_okf import Bundle, OKFTools
from astromesh_okf.tools import DESCRIPTIONS, PARAMS, TOOL_NAMES

FIX = Path(__file__).resolve().parent / "fixtures" / "okf"


def test_accepts_bundle_str_or_path():
    for b in (Bundle(FIX), str(FIX), FIX):
        assert OKFTools(b).kb_index().startswith("# Subdirectories")


def test_kb_read_returns_json_string():
    out = json.loads(OKFTools(FIX).kb_read("metrics/revenue"))
    assert out["title"] == "Revenue"
    assert out["trust"] == "machine-confirmed"


def test_errors_are_json_never_raised():
    out = json.loads(OKFTools(FIX).kb_read("../outside"))
    assert out["error"].startswith("outside bundle: ")
    out = json.loads(OKFTools(FIX).kb_read("metrics/revenu"))
    assert out["error"].startswith("concept not found: metrics/revenu (did you mean: ")


def test_kb_find_coerces_loose_arguments():
    t = OKFTools(FIX)
    out = json.loads(t.kb_find(type="Metric", tags="finance", limit="2"))
    assert [r["id"] for r in out["results"]] == ["metrics/gross-margin", "metrics/revenue"]
    assert json.loads(t.kb_find(limit="many"))["results"]
    assert json.loads(t.kb_find(limit=float("inf")))["results"]
    ids = [r["id"] for r in json.loads(t.kb_find(include_deprecated="true"))["results"]]
    assert "metrics/gross-margin-legacy" in ids
    ids = [r["id"] for r in json.loads(t.kb_find(include_deprecated="false"))["results"]]
    assert "metrics/gross-margin-legacy" not in ids
    assert "results" in json.loads(t.kb_find(text=5, type=7, tags=["finance", 1]))


def test_non_ascii_is_kept_readable(tmp_path):
    (tmp_path / "c.md").write_text(
        "---\ntype: Nota\ntitle: Política de reembolsos\n---\nÜber 日本\n"
    )
    raw = OKFTools(tmp_path).kb_read("c")
    assert "Política de reembolsos" in raw
    assert "日本" in raw


def test_names_and_prefix():
    assert OKFTools(FIX).names == ["kb_index", "kb_read", "kb_find"]
    assert OKFTools(FIX, prefix="acme_").names == ["acme_kb_index", "acme_kb_read", "acme_kb_find"]


def test_functions_are_named_documented_and_typed():
    fns = OKFTools(FIX, prefix="acme_").functions()
    assert [f.__name__ for f in fns] == ["acme_kb_index", "acme_kb_read", "acme_kb_find"]
    assert [f.okf_name for f in fns] == list(TOOL_NAMES)
    for f in fns:
        assert DESCRIPTIONS[f.okf_name] in f.__doc__
        assert "Args:" in f.__doc__
        params = list(inspect.signature(f).parameters)
        assert params == [p.name for p in PARAMS[f.okf_name]]
    assert fns[0]().startswith("# Subdirectories")
    assert json.loads(fns[1]("metrics/revenue"))["id"] == "metrics/revenue"


def test_importing_the_package_imports_no_framework():
    import astromesh_okf  # noqa: F401

    for mod in (
        "langchain_core",
        "crewai",
        "google.adk",
        "agents",
        "pydantic_ai",
        "llama_index",
        "smolagents",
        "agent_framework",
        "mcp",
    ):
        assert mod not in sys.modules, mod

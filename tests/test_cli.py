import importlib
import json
from pathlib import Path

import pytest

from astromesh_okf import __version__
from astromesh_okf.cli import main

FIX = Path(__file__).resolve().parent / "fixtures" / "okf"


def test_index_read_find(capsys):
    assert main(["index", str(FIX)]) == 0
    assert capsys.readouterr().out.startswith("# Subdirectories")
    assert main(["read", str(FIX), "metrics/revenue"]) == 0
    assert json.loads(capsys.readouterr().out)["title"] == "Revenue"
    assert main(["find", str(FIX), "--type", "Metric", "--tag", "finance"]) == 0
    ids = [r["id"] for r in json.loads(capsys.readouterr().out)["results"]]
    assert ids == ["metrics/gross-margin", "metrics/revenue"]


def test_missing_bundle_dir_is_an_error(capsys, tmp_path):
    assert main(["index", str(tmp_path / "nope")]) == 2
    assert "not a directory" in capsys.readouterr().err


def test_mcp_without_the_extra_is_a_clean_error(monkeypatch, capsys):
    real = importlib.import_module

    def fake(name, *a, **k):
        if name.startswith("mcp"):
            raise ImportError("no mcp")
        return real(name, *a, **k)

    monkeypatch.setattr(importlib, "import_module", fake)
    assert main(["mcp", str(FIX)]) == 2
    err = capsys.readouterr().err
    assert "pip install 'astromesh-okf[mcp]'" in err
    assert "Traceback" not in err


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out == f"astromesh-okf {__version__}\n"

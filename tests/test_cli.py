import json
from pathlib import Path

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

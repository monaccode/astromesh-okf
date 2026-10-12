import py_compile
import runpy
from pathlib import Path

from astromesh_okf import Bundle

EX = Path(__file__).resolve().parents[1] / "examples"


def test_examples_compile():
    for script in EX.glob("*.py"):
        py_compile.compile(str(script), doraise=True)


def test_sample_bundle_is_conformant():
    res = Bundle(EX / "bundles" / "support").find(include_deprecated=True)
    assert res["skipped_invalid"] == 0
    assert len(res["results"]) == 3


def test_plain_python_example_runs(capsys):
    runpy.run_path(str(EX / "plain_python.py"), run_name="__main__")
    assert "Refund policy" in capsys.readouterr().out

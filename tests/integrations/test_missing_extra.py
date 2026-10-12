import importlib

import pytest

from astromesh_okf.integrations._base import require


def test_missing_framework_names_the_extra(monkeypatch):
    real = importlib.import_module

    def fake(name, *a, **k):
        if name.startswith("crewai"):
            raise ImportError("no crewai")
        return real(name, *a, **k)

    monkeypatch.setattr(importlib, "import_module", fake)
    with pytest.raises(ImportError, match=r"pip install 'astromesh-okf\[crewai\]'"):
        require("crewai.tools", "crewai")


def test_pydantic_ai_names_the_python_floor(monkeypatch):
    def fake(name, *a, **k):
        raise ImportError("no pydantic_ai")

    monkeypatch.setattr(importlib, "import_module", fake)
    with pytest.raises(ImportError, match=r"\(requires Python >= 3\.11\)$"):
        require("pydantic_ai", "pydantic-ai")

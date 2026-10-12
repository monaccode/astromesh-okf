import builtins

import pytest

from astromesh_okf.integrations._base import require


def test_missing_framework_names_the_extra(monkeypatch):
    real = builtins.__import__

    def fake(name, *a, **k):
        if name.startswith("crewai"):
            raise ImportError("no crewai")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake)
    with pytest.raises(ImportError, match=r"pip install 'astromesh-okf\[crewai\]'"):
        require("crewai.tools", "crewai")

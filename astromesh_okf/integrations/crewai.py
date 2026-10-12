"""CrewAI tools for an OKF bundle (BaseTool subclasses with an explicit args schema)."""

from __future__ import annotations

from astromesh_okf.integrations._base import py_type, require
from astromesh_okf.tools import DESCRIPTIONS, PARAMS, OKFTools


def okf_tools(bundle, prefix: str = "") -> list:
    tools = require("crewai.tools", "crewai")
    pydantic = require("pydantic", "crewai")
    out = []
    for fn in OKFTools(bundle, prefix).functions():
        fields = {
            p.name: (
                py_type(p),
                pydantic.Field(... if p.required else p.default, description=p.description),
            )
            for p in PARAMS[fn.okf_name]
        }
        args_model = pydantic.create_model(f"{fn.__name__}_args", **fields)

        class _OKFTool(tools.BaseTool):
            name: str = fn.__name__
            description: str = DESCRIPTIONS[fn.okf_name]
            args_schema: type[pydantic.BaseModel] = args_model

            def _run(self, _fn=fn, **kwargs) -> str:
                return _fn(**kwargs)

        out.append(_OKFTool())
    return out

"""smolagents Tools for an OKF bundle."""

from __future__ import annotations

from astromesh_okf.integrations._base import require
from astromesh_okf.tools import DESCRIPTIONS, PARAMS, OKFTools


def okf_tools(bundle, prefix: str = "") -> list:
    smol = require("smolagents", "smolagents")
    out = []
    for fn in OKFTools(bundle, prefix).functions():
        # A different name than the class attribute: inside a class body, `inputs = inputs`
        # would look `inputs` up in the class namespace, not in this function.
        _inputs = {
            p.name: {"type": p.type, "description": p.description}
            | ({} if p.required else {"nullable": True})
            for p in PARAMS[fn.okf_name]
        }

        class _OKFTool(smol.Tool):
            name = fn.__name__
            description = DESCRIPTIONS[fn.okf_name]
            inputs = _inputs
            output_type = "string"
            # forward takes **kwargs, so its signature can't match `inputs` literally
            skip_forward_signature_validation = True

            def forward(self, _fn=fn, **kwargs):
                return _fn(**{k: v for k, v in kwargs.items() if v is not None})

        out.append(_OKFTool())
    return out

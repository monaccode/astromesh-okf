"""The three tools an agent uses to navigate an OKF bundle, independent of any framework.

Every tool returns a string (most frameworks expect text back from a tool) and never raises:
an error comes back as the JSON string {"error": "..."} so the model can correct itself.

The signatures use typing.Optional on purpose (no `from __future__ import annotations`, no
`X | None`): Google ADK's schema builder rejects PEP 604 unions (verified on google-adk 1.14).
"""

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional, Union

from astromesh_okf.bundle import Bundle
from astromesh_okf.concept import BundleError

TOOL_NAMES = ("kb_index", "kb_read", "kb_find")

DESCRIPTIONS = {
    "kb_index": (
        "List a directory of the knowledge bundle. Start here with path '/'. Links starting "
        "with '/' are bundle-absolute; other links in an index are relative to the listed "
        "directory."
    ),
    "kb_read": (
        "Read one concept of the knowledge bundle: metadata, trust warnings, body, and its "
        "links already resolved to concept ids you can pass back to kb_read."
    ),
    "kb_find": (
        "Search concepts of the knowledge bundle by type, tags (all must match) and text. "
        "Deprecated concepts are excluded unless include_deprecated is true."
    ),
}


@dataclass(frozen=True)
class Param:
    name: str
    type: str  # "string" | "array" | "boolean" | "integer"
    description: str
    default: object = None
    required: bool = False


PARAMS: dict[str, tuple[Param, ...]] = {
    "kb_index": (Param("path", "string", "Directory inside the bundle; '/' is the root.", "/"),),
    "kb_read": (
        Param(
            "concept_id",
            "string",
            "Concept id such as 'metrics/revenue' (a leading '/' and '.md' are accepted).",
            required=True,
        ),
    ),
    "kb_find": (
        Param("text", "string", "Text to look for in title, description, tags and body."),
        Param("type", "string", "Exact concept type, case-insensitive (e.g. 'Metric')."),
        Param("tags", "array", "Tags the concept must all have."),
        Param("include_deprecated", "boolean", "Also return deprecated concepts.", False),
        Param("limit", "integer", "Maximum number of results (1-100).", 20),
    ),
}


def _int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _bool(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def _str_or_none(value):
    return None if value is None else str(value)


def _tags(tags):
    # Models send tags as a string or with non-string items; normalize here, not in Bundle.
    if isinstance(tags, str):
        return [tags]
    if isinstance(tags, (list, tuple)):
        return [str(t) for t in tags]
    return None


def _run(fn, *args, **kwargs) -> str:
    try:
        data = fn(*args, **kwargs)
    except BundleError as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)
    # permissions, a file vanishing between listing and reading, or a stray ValueError
    except (OSError, ValueError) as exc:
        # never str(exc): an OSError carries the absolute path of the file
        reason = getattr(exc, "strerror", None) or type(exc).__name__
        return json.dumps({"error": f"bundle read failed: {reason}"}, ensure_ascii=False)
    return data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)


def _docstring(base: str) -> str:
    args = "\n".join(f"    {p.name}: {p.description}" for p in PARAMS[base])
    return f"{DESCRIPTIONS[base]}\n\nArgs:\n{args}\n"


class OKFTools:
    """kb_index / kb_read / kb_find over one bundle. `prefix` renames them (two bundles, one agent)."""

    def __init__(self, bundle: Union[Bundle, str, os.PathLike], prefix: str = ""):
        self.bundle = bundle if isinstance(bundle, Bundle) else Bundle(bundle)
        self.prefix = prefix

    @property
    def names(self) -> list[str]:
        return [self.prefix + n for n in TOOL_NAMES]

    def kb_index(self, path: str = "/") -> str:
        return _run(self.bundle.index, "/" if path is None else str(path))

    def kb_read(self, concept_id: str) -> str:
        return _run(self.bundle.read, "" if concept_id is None else str(concept_id))

    def kb_find(
        self,
        text: Optional[str] = None,
        type: Optional[str] = None,  # the model-facing name
        tags: Optional[list[str]] = None,
        include_deprecated: bool = False,
        limit: int = 20,
    ) -> str:
        return _run(
            self.bundle.find,
            text=_str_or_none(text),
            type_=_str_or_none(type),
            tags=_tags(tags),
            include_deprecated=_bool(include_deprecated),
            limit=_int(limit, 20),
        )

    def functions(self) -> list[Callable[..., str]]:
        """Plain functions, named with the prefix and documented for the model.

        Adapters wrap these: most frameworks build the tool schema from the signature and
        the Google-style docstring.
        """

        def kb_index(path: str = "/") -> str:
            return self.kb_index(path)

        def kb_read(concept_id: str) -> str:
            return self.kb_read(concept_id)

        def kb_find(
            text: Optional[str] = None,
            type: Optional[str] = None,
            tags: Optional[list[str]] = None,
            include_deprecated: bool = False,
            limit: int = 20,
        ) -> str:
            return self.kb_find(text, type, tags, include_deprecated, limit)

        out = []
        for fn, base in zip((kb_index, kb_read, kb_find), TOOL_NAMES, strict=True):
            fn.__name__ = fn.__qualname__ = self.prefix + base
            fn.__doc__ = _docstring(base)
            fn.okf_name = base
            out.append(fn)
        return out

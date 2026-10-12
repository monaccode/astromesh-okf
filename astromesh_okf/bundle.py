"""Read-only access to an OKF bundle on disk: index, read and find, confined to its root."""

from __future__ import annotations

import difflib
import logging
import re
from datetime import datetime
from pathlib import Path

from astromesh_okf.concept import (
    MAX_FIND_LIMIT,
    RESERVED,
    BundleError,
    Concept,
    InvalidConceptError,
    _id_of,
    parse_concept,
    split_frontmatter,
)

logger = logging.getLogger(__name__)


class OutsideBundleError(BundleError):
    """The requested path resolves outside the bundle root."""


class ConceptNotFoundError(BundleError):
    """No concept has that ID."""


class NotAConceptError(BundleError):
    """The path exists but is not a concept (directory, reserved or non-markdown)."""


# Markdown links (§6.1). Excludes images (`![...]`); footnotes (`[^id]`) have no
# parentheses and do not match.
_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(\s*([^)\s]+)[^)]*\)")
_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _clean(raw: str) -> str:
    """Normalize what the model sends: no `#...` fragment and no leading `/`."""
    return str(raw or "").split("#", 1)[0].strip().lstrip("/")


def _strip_frontmatter(text: str) -> str:
    """An `index.md` only carries frontmatter at the root (`okf_version`, §12); drop it."""
    try:
        return split_frontmatter(text)[1]
    except InvalidConceptError:
        return text


def _index_line(c: Concept) -> str:
    flags = [c.type]
    if c.status != "stable":
        flags.append(c.status)
    if c.stale:
        flags.append("stale")
    desc = f" - {c.description}" if c.description else ""
    return f"* [{c.title}](/{c.id}){desc} [{', '.join(flags)}]"


def _log_skipped(count: int, where: str) -> None:
    logger.warning("okf: skipped %d invalid concept(s) in %s", count, where)


class Bundle:
    """An OKF bundle on disk, read-only. Reads on every call: no cache."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def _inside(self, rel: str, raw: str) -> Path:
        # `resolve` follows symlinks BEFORE the check: a link pointing outside does not pass.
        try:
            path = (self.root / rel).resolve()
        except (OSError, ValueError):
            raise OutsideBundleError(f"outside bundle: {raw}") from None
        if not path.is_relative_to(self.root):
            raise OutsideBundleError(f"outside bundle: {raw}")
        return path

    def _concept_path(self, raw: str) -> Path:
        rel = _clean(raw)
        base = self.root / rel
        # `.md` is appended before resolving: otherwise a symlink `x.md` would be checked
        # as `x` (which does not exist) and read anyway.
        try:
            exists = base.exists()
        except (OSError, ValueError):
            exists = False
        if rel and not rel.endswith(".md") and not exists:
            rel += ".md"
        return self._inside(rel, raw)

    def _concept_files(self) -> list[Path]:
        out = []
        for path in self.root.rglob("*.md"):
            rel_parts = path.relative_to(self.root).parts
            if path.name in RESERVED or any(p.startswith(".") for p in rel_parts):
                continue
            if path.is_file() and path.resolve().is_relative_to(self.root):
                out.append(path)
        return sorted(out, key=lambda p: _id_of(self.root, p))

    def _not_found(self, cid: str) -> str:
        ids = [_id_of(self.root, p) for p in self._concept_files()]
        close = difflib.get_close_matches(cid, ids, n=3)
        msg = f"concept not found: {cid}"
        return f"{msg} (did you mean: {', '.join(close)}?)" if close else msg

    def read(self, concept_id: str, now: datetime | None = None) -> dict:
        path = self._concept_path(concept_id)
        cid = _id_of(self.root, path)
        try:
            exists = path.exists()
            is_dir = path.is_dir()
        except (OSError, ValueError):
            raise OutsideBundleError(f"outside bundle: {concept_id}") from None
        if not exists:
            raise ConceptNotFoundError(self._not_found(cid))
        if is_dir or path.suffix != ".md" or path.name in RESERVED:
            raise NotAConceptError(f"not a concept: {cid}")
        concept = parse_concept(self.root, path, now)
        return {
            **concept.summary(),
            "tags": concept.tags,
            "warnings": concept.warnings,
            "extra": concept.extra,
            "body": concept.body,
            "links": self._links(path, concept.body),
        }

    def _links(self, path: Path, body: str) -> list[dict]:
        """Body links resolved to IDs, so the model need not compute relative paths."""
        out, seen = [], set()
        for target in _LINK.findall(body):
            if _SCHEME.match(target):
                item, key = {"url": target, "external": True}, target
            else:
                raw = target.split("#", 1)[0]
                if not raw:
                    continue  # anchor within the same concept
                try:
                    base = self.root if raw.startswith("/") else path.parent
                    dest = (base / raw.lstrip("/")).resolve()
                    if not dest.is_relative_to(self.root):
                        continue
                    if raw.endswith("/") or dest.is_dir() or dest.name == "index.md":
                        folder = dest.parent if dest.name == "index.md" else dest
                        item = {
                            "id": _id_of(self.root, folder),
                            "dir": True,
                            "exists": folder.is_dir(),
                        }
                    else:
                        item = {"id": _id_of(self.root, dest), "exists": dest.is_file()}
                except (OSError, ValueError):
                    continue  # impossible name on this filesystem: skip the link
                key = item["id"]
            if key not in seen:
                seen.add(key)
                out.append(item)
        return out

    def index(self, path: str = "/", now: datetime | None = None) -> str:
        folder = self._inside(_clean(path), path)
        if not folder.is_dir():
            raise BundleError(f"not a directory: {path}")
        existing = folder / "index.md"
        if existing.is_file() and existing.resolve().is_relative_to(self.root):
            try:
                return _strip_frontmatter(existing.read_text(encoding="utf-8-sig"))
            except (UnicodeDecodeError, OSError):
                raise BundleError(f"invalid index: {path}") from None
        return self._synth_index(folder, now)

    def _synth_index(self, folder: Path, now: datetime | None) -> str:
        """Index in the §8 format when the directory has no `index.md`."""
        lines: list[str] = []
        subdirs = sorted(
            p
            for p in folder.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.resolve().is_relative_to(self.root)
        )
        if subdirs:
            lines += ["# Subdirectories", ""]
            lines += [f"* [{p.name}](/{_id_of(self.root, p)}/)" for p in subdirs]
        concepts, skipped = [], 0
        for path in folder.glob("*.md"):
            if path.name in RESERVED or not path.resolve().is_relative_to(self.root):
                continue
            if not path.is_file():
                continue
            try:
                concepts.append(parse_concept(self.root, path, now))
            except InvalidConceptError:
                skipped += 1
        if concepts:
            if lines:
                lines.append("")
            lines += ["# Concepts", ""]
            lines += [_index_line(c) for c in sorted(concepts, key=lambda c: c.id)]
        if skipped:
            _log_skipped(skipped, _id_of(self.root, folder))
            lines += ["", f"({skipped} concept(s) skipped: invalid frontmatter)"]
        return "\n".join(lines) + "\n" if lines else "(empty directory)\n"

    def find(
        self,
        text: str | None = None,
        type_: str | None = None,
        tags: list[str] | None = None,
        include_deprecated: bool = False,
        limit: int = 20,
        now: datetime | None = None,
    ) -> dict:
        # ponytail: walks and parses every file on each call; fine for hundreds to a few
        # thousand concepts. Beyond that, ingest into a real index (RAG).
        limit = max(1, min(int(limit), MAX_FIND_LIMIT))
        want_tags = {t.lower() for t in tags or []}
        needle = text.lower() if text else None
        header_hits, body_hits, skipped = [], [], 0
        for path in self._concept_files():
            try:
                c = parse_concept(self.root, path, now)
            except InvalidConceptError:
                skipped += 1
                continue
            if c.status == "deprecated" and not include_deprecated:
                continue
            if type_ and c.type.lower() != type_.lower():
                continue
            if not want_tags <= {t.lower() for t in c.tags}:
                continue
            if needle is None or needle in " ".join([c.title, c.description, *c.tags]).lower():
                header_hits.append(c)
            elif needle in c.body.lower():
                body_hits.append(c)
        if skipped:
            _log_skipped(skipped, "/")
        hits = (header_hits + body_hits)[:limit]
        return {"results": [c.summary() for c in hits], "skipped_invalid": skipped}

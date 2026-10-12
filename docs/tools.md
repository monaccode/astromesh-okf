# Tools reference

`OKFTools(bundle, prefix="")` exposes three tools. `bundle` is a `Bundle`, a `str` or a
`PathLike`. Every tool returns a `str` and never raises; every framework adapter wraps these
same three functions.

```python
from astromesh_okf import OKFTools

kb = OKFTools("./my-bundle", prefix="acme_")
kb.names  # ['acme_kb_index', 'acme_kb_read', 'acme_kb_find']
kb_index, kb_read, kb_find = kb.functions()  # plain functions named with the prefix
```

The descriptions the model sees are in `astromesh_okf.DESCRIPTIONS`, and the argument
schema in `astromesh_okf.PARAMS`.

## kb_index

> List a directory of the knowledge bundle. Start here with path '/'. Links starting with
> '/' are bundle-absolute; other links in an index are relative to the listed directory.

| Argument | Type | Default | Notes |
|---|---|---|---|
| `path` | string | `"/"` | directory inside the bundle; a leading `/` and a `#fragment` are ignored |

Returns Markdown: the directory's `index.md` with its frontmatter removed, or a synthesized
index:

```markdown
# Subdirectories

* [policies](/policies/)

# Concepts

* [Plans](/plans) - The three subscription plans. [Reference, stale]

(1 concept(s) skipped: invalid frontmatter)
```

Each synthesized concept line ends with its type, its status when not `stable`, and `stale`
when stale. An empty directory returns `(empty directory)`.

For the root, `Bundle(path).index("/")` returns the same text: put it in the system prompt.

## kb_read

> Read one concept of the knowledge bundle: metadata, trust warnings, body, and its links
> already resolved to concept ids you can pass back to kb_read.

| Argument | Type | Default | Notes |
|---|---|---|---|
| `concept_id` | string | required | e.g. `metrics/revenue`; `/metrics/revenue`, `metrics/revenue.md` and a `#fragment` are accepted |

Returns a JSON object:

| Key | Type | Notes |
|---|---|---|
| `id`, `type`, `title`, `description` | string | |
| `status` | string | lowercased, `stable` by default |
| `trust` | string | `unverified`, `machine-confirmed` or `human-reviewed` |
| `stale` | bool | |
| `tags` | list of strings | |
| `warnings` | list of strings | see [concepts](concepts.md#trust-and-freshness) |
| `extra` | object | every other frontmatter field, dates as ISO 8601 strings |
| `body` | string | Markdown after the frontmatter |
| `links` | list | `{"id", "exists"}`, `{"id", "dir": true, "exists"}` or `{"url", "external": true}`, deduplicated, in order of appearance |

## kb_find

> Search concepts of the knowledge bundle by type, tags (all must match) and text.
> Deprecated concepts are excluded unless include_deprecated is true.

| Argument | Type | Default | Notes |
|---|---|---|---|
| `text` | string | none | case-insensitive substring of title, description, tags or body |
| `type` | string | none | exact type, case-insensitive |
| `tags` | list of strings | none | the concept must have all of them (case-insensitive) |
| `include_deprecated` | bool | `false` | |
| `limit` | int | `20` | clamped to 1–100 |

Returns:

```json
{"results": [{"id": "policies/refunds", "type": "Policy", "title": "Refund policy",
  "description": "Customers can ask for a full refund within 30 days of purchase.",
  "status": "stable", "trust": "human-reviewed", "stale": false}],
 "skipped_invalid": 0}
```

Concepts whose title, description or tags match `text` come before those that match only
in the body; within each group, results are ordered by id. With no `text`, every concept
that passes the other filters matches. `skipped_invalid` counts invalid concept files met
during the scan. Hidden files, dot-directories, `index.md` and `log.md` are never searched.

`kb_find` reads and parses every concept file on each call.

## Argument coercion

Models send loose arguments. The tools accept them:

| Received | Used as |
|---|---|
| `limit="2"` | `2` |
| `limit="many"`, `limit=None`, `limit=inf` | `20` |
| `tags="finance"` | `["finance"]` |
| `tags=["finance", 1]` | `["finance", "1"]` |
| `include_deprecated="true"` / `"1"` / `"yes"` | `true`; any other string is `false` |
| `text=5`, `type=7` | `"5"`, `"7"` |
| `path=None` | `"/"` |

## Errors

Errors are returned as `{"error": "<message>"}`:

| Message | Raised as (in `Bundle`) | When |
|---|---|---|
| `outside bundle: <input>` | `OutsideBundleError` | the path resolves outside the root, symlinks followed; also impossible names (NUL bytes, names too long) |
| `concept not found: <id>` | `ConceptNotFoundError` | no such file; with ` (did you mean: a, b?)` listing up to three close ids |
| `not a concept: <id>` | `NotAConceptError` | a directory, `index.md`/`log.md`, or a file that is not `.md` |
| `not a directory: <path>` | `BundleError` | `kb_index` on a file or a missing directory |
| `invalid index: <path>` | `BundleError` | the directory's `index.md` is not UTF-8 or cannot be read |
| `invalid concept <id>: <reason>` | `InvalidConceptError` | `missing frontmatter`, `unterminated frontmatter`, `unparseable frontmatter (<YAML error class>)`, `frontmatter is not a mapping`, `missing type`, `not UTF-8`, `unreadable (<OS error class>)` |
| `bundle read failed: <detail>` | `OSError` / `ValueError` | anything else that goes wrong reading the disk |

All `Bundle` errors subclass `BundleError`, which subclasses `ValueError`. Use `Bundle`
directly when you want exceptions and Python objects instead of strings:

```python
from astromesh_okf import Bundle, ConceptNotFoundError

bundle = Bundle("./my-bundle")
try:
    concept = bundle.read("policies/refunds")  # dict
except ConceptNotFoundError as exc:
    print(exc)
hits = bundle.find(type_="Policy", tags=["refunds"])  # note: type_
```

## Prefixes

`prefix` is prepended to each tool name, so one agent can use several bundles:

```python
from astromesh_okf.integrations.langchain import okf_tools

tools = okf_tools("./support-kb", prefix="support_") + okf_tools("./finance-kb", prefix="finance_")
```

Say in the system prompt which bundle holds what.

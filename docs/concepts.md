# OKF in two minutes

The [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
(OKF) v0.2 describes knowledge as plain files. This page covers what `astromesh-okf` reads;
the spec is the authority.

## Bundle

A bundle is a directory. Everything inside it is addressed relative to its root:

```
support/
  index.md              # optional: the root index (may carry okf_version)
  policies/
    refunds.md          # concept "policies/refunds"
    refunds-2024.md     # concept "policies/refunds-2024"
  products/
    plans.md            # concept "products/plans"
```

That tree is [examples/bundles/support](../examples/bundles/support/index.md).

## Concept

A concept is one Markdown file with YAML frontmatter. Its **id** is its path inside the
bundle without `.md`, always with forward slashes (`policies/refunds`).

```markdown
---
type: Policy
title: Refund policy
description: Customers can ask for a full refund within 30 days of purchase.
tags: [support, refunds]
status: stable
generated: { by: human:support-lead, at: 2026-09-01T12:00:00Z }
verified: { by: human:support-lead, at: 2026-09-01T12:00:00Z }
stale_after: 2030-09-01T00:00:00Z
---

# Rule

A full refund is available within 30 days of purchase for every plan in
[plans](/products/plans.md). After 30 days, refunds are prorated for annual plans only.
```

Only `type` is required. A file without parseable frontmatter (or whose frontmatter is not
a mapping) or without `type` is invalid; indexes and search skip it and count it. Any field
the library does not map (`generated`, `verified`, your own) is returned in `extra`.

YAML anchors and aliases (`&name` / `*name`, including merge keys `<<: *name`) are rejected:
a concept that uses them is invalid. Aliases let a few bytes expand into gigabytes or a
self-referencing structure, and a bundle may come from someone you do not control.

## Frontmatter the library uses

| Field | Meaning | Default |
|---|---|---|
| `type` | what kind of thing this is (`Policy`, `Metric`, `Table`...) | required |
| `title` | display name | the file name |
| `description` | one line | empty |
| `tags` | list of strings (a single string is accepted) | `[]` |
| `status` | `stable`, `draft` or `deprecated` | `stable` |
| `verified` | one event or a list of events `{by, at}` | unverified |
| `stale_after` | date or datetime after which the concept may be outdated | never stale |

`generated` (`{by, at}` provenance) and v0.1's `timestamp` are not interpreted: they are
passed through in `extra`. (`verified` is both: it sets `trust` and is also in `extra`.)

## Links

Concepts link to each other with ordinary Markdown links. A link starting with `/` is
bundle-absolute; anything else is relative to the concept's directory. `kb_read` resolves
them for the model:

```json
"links": [{"id": "products/plans", "exists": true}, {"id": "policies/refunds-2024", "exists": true}]
```

Directories come back with `"dir": true`, external URLs as `{"url": ..., "external": true}`,
anchors inside the same concept are skipped, images are not links, and links that leave the
bundle are dropped.

## index.md and log.md

`index.md` and `log.md` are reserved names, never concepts. A directory's `index.md` is
what `kb_index` returns for it (without frontmatter). When a directory has none, the library
synthesizes one in the spec's format:

```markdown
# Concepts

* [Refund policy](/policies/refunds) - Customers can ask for a full refund within 30 days of purchase. [Policy]
* [Refund policy (2024)](/policies/refunds-2024) - Retired 14-day refund window. [Policy, deprecated]
```

`log.md` is not read by any tool.

## Trust and freshness

Every concept the tools return carries four signals:

- **`trust`**: `human-reviewed` if any `verified` event has a `by` starting with `human:`,
  `machine-confirmed` if some event has another `by` (for example `process:catalog-export`),
  `unverified` otherwise.
- **`stale`**: `true` when the current time is at or past `stale_after`. A date counts as
  midnight UTC; a datetime without a timezone counts as UTC; an unreadable value is ignored
  and logged.
- **`status`**: lowercased; `stable` when absent.
- **`warnings`** (in `kb_read`): one sentence per problem, for the model to repeat:
  - `DEPRECATED: kept for history; do not use for new work.`
  - `STALE since 2030-09-01T00:00:00+00:00: may no longer be accurate.`
  - `DRAFT: not reviewed; may be incomplete.`

The signals annotate; they never hide a concept from `kb_read` or `kb_index`. Only
`kb_find` leaves deprecated concepts out by default.

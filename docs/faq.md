# FAQ

### How big can a bundle be?

There is no hard limit, but there is no index either. `kb_read` and `kb_index` touch one
file or one directory. `kb_find` walks the whole bundle and parses every concept on each
call: comfortable for hundreds to a few thousand concepts, slow beyond that. If your
knowledge is that big and unstructured, it is a job for RAG; see the next question.

### Can I use it together with RAG?

Yes. Give the agent both: a retriever for the large unstructured corpus and the OKF tools
for the curated, linked core (policies, definitions, runbooks). Say in the system prompt
which to use for what. The OKF tools are ordinary tools, so they sit next to any retriever
tool your framework offers.

### Can one agent use several bundles?

Yes, with `prefix`:

```python
from astromesh_okf.integrations.langchain import okf_tools

tools = okf_tools("./support-kb", prefix="support_") + okf_tools("./finance-kb", prefix="finance_")
```

The tools become `support_kb_index`, `finance_kb_read` and so on. Put each bundle's root
index in the system prompt under a heading that says what it covers.

### Can I read a bundle from git, a tarball or a URL?

Not yet: a bundle is a local directory. Clone or extract it first (for example
`git clone --depth 1 <repo> ./kb`) and point the tools at the directory. Remote bundles are
on the roadmap.

### Does it cache? Will the agent see edits?

No cache. Every tool call reads the files, so an edit is visible on the next call. The only
thing that can go stale is a root index you copied into the system prompt; rebuild the
prompt when the bundle's structure changes.

### What happens with Attested Computations?

Their concepts are Markdown like any other, so `kb_read` returns them, frontmatter
included (in `extra`). Nothing is ever executed: the library only reads `.md` files, and
asking for a script that sits next to a concept (say `attesters/check.py`) returns
`not a concept: attesters/check.py`. If you want the computation re-run, that is your
code's decision, outside this library.

### Why doesn't `kb_find` return deprecated concepts?

A search result reads as a recommendation, and a retired policy should not be one. Pass
`include_deprecated=true` to include them. `kb_read` and `kb_index` always show deprecated
concepts, with a `DEPRECATED` warning, so the model can still follow a link to history.

### What about Windows paths and file encodings?

Concept ids always use forward slashes (`policies/refunds`), on every OS, and that is what
the model should send back. Files are read as UTF-8 regardless of the system locale; a
UTF-8 byte-order mark is accepted, and a file in another encoding is an invalid concept
(`not UTF-8`), skipped by index and search. CI runs on Linux; Windows is not tested in CI
yet, so reports are welcome.

### Google ADK logs "Default value is not supported in function declaration schema for Google AI." Is that a problem?

No. ADK cannot send defaults to Gemini in the schema, so it warns and drops them; the
tools apply their own defaults when an argument is missing.

### The model keeps sending `"2"` or `"false"` as strings. Do I need to fix my prompt?

No. The tools coerce loose arguments: numeric strings become numbers, a single tag becomes
a list, and `"true"`/`"1"`/`"yes"` mean true. See
[argument coercion](tools.md#argument-coercion).

### Is it safe to mount a bundle I didn't write?

The tools cannot leave the bundle directory (symlinks are resolved before checking) and
never write or execute anything. But concept text goes into the model's context like any
tool result, so a malicious bundle can attempt prompt injection. Mount only bundles you
trust.

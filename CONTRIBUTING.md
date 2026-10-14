# Contributing

Thanks for helping. Bug reports with a small bundle that reproduces the problem are the
most useful contribution there is.

## Setup

You need [uv](https://docs.astral.sh/uv/). `uv.lock` is committed and CI installs with
`--locked`, so run `uv lock` and commit the lock whenever you change `pyproject.toml`.

```bash
git clone https://github.com/monaccode/astromesh-okf
cd astromesh-okf
uv sync
```

## Tests

```bash
uv run pytest -q                       # core: no framework installed, adapter tests skip
uv run --python 3.10 pytest -q         # the oldest supported Python
```

Each adapter is tested against the real framework, without calling a model. Install one
extra at a time, as CI does (frameworks have conflicting dependencies):

```bash
uv run --extra langchain pytest tests/integrations/test_langchain.py -q
uv run --extra pydantic-ai --python 3.12 pytest tests/integrations/test_pydantic_ai.py -q
```

Against Google's sample bundles:

```bash
git clone --depth 1 https://github.com/GoogleCloudPlatform/open-knowledge-format /tmp/okf
uv run python scripts/check_google_samples.py /tmp/okf
```

## Lint

```bash
uv run ruff check .
uv run ruff format --check .   # CI gate; also formats Python blocks inside Markdown
uv run ruff format .           # writes the fix
```

## Commits

[Conventional commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`,
`test:`, `chore:`. Add user-visible changes to `CHANGELOG.md` under `[Unreleased]`.

## Adding a framework adapter

1. **Module.** Create `astromesh_okf/integrations/<framework>.py` with
   `okf_tools(bundle, prefix: str = "") -> list`. Import the framework with
   `require("<module>", "<extra>")` inside the function (never at module level), and wrap
   `OKFTools(bundle, prefix).functions()`, using `DESCRIPTIONS[fn.okf_name]` for the
   description. If the framework cannot derive a schema from the signature, build one from
   `PARAMS` (see `crewai.py` and `smolagents.py`).
2. **Extra.** Add `<extra> = ["<package>>=<version you tested>"]` to
   `[project.optional-dependencies]` (a floor, no ceiling) and run `uv lock`.
3. **Test.** Add `tests/integrations/test_<framework>.py` with `pytest.importorskip`: build
   the tools, check names and schema, and invoke each tool without a model. Add the module
   to `test_importing_the_package_imports_no_framework` and a row to the `extras` matrix in
   `.github/workflows/ci.yml`.
4. **Docs.** Add `examples/<framework>_agent.py` (importing it must not call a model), a
   row to `examples/README.md`, a row and snippet to `README.md` and `README.es.md`, and a
   section to `docs/integrations.md`.

## Releasing (maintainers)

1. Bump `version` in `pyproject.toml` and `__version__` in `astromesh_okf/__init__.py`, run
   `uv lock`, and move `[Unreleased]` in `CHANGELOG.md` to a dated version section.
2. Tag `vX.Y.Z` and push the tag. `.github/workflows/release.yml` runs the tests and lint,
   checks that the tag matches the version, builds with `uv build`, publishes to TestPyPI,
   installs that build from TestPyPI and runs the CLI against the sample bundle, and only then
   publishes to PyPI. Both uploads use trusted publishing and skip files that already exist,
   so re-running a release is safe. The workflow can also be started by hand from `main`
   (`workflow_dispatch`), e.g. to put an already-published version on TestPyPI.

Trusted publishing needs a one-time setup by a maintainer, on both indexes: register a
publisher for the `astromesh-okf` project with owner `monaccode`, repository
`astromesh-okf` and workflow `release.yml` — environment `testpypi` on test.pypi.org and
environment `pypi` on pypi.org — and create both environments in the GitHub repository
settings. Until then the workflow fails at the matching publish step.

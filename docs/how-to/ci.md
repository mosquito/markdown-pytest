# How to run Markdown tests in CI

Adding Markdown tests to continuous integration ensures that documentation
examples are verified on every push. This page shows configurations for the
most common CI platforms.

## GitHub Actions

### Minimal workflow

```{code-block} yaml
# .github/workflows/docs-tests.yml
name: docs-tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install markdown-pytest
      - run: pytest -v README.md
```

### Combined with existing tests

```{code-block} yaml
- run: pip install markdown-pytest pytest
- run: pytest -v tests/ README.md docs/
```

### Matrix over Python versions

```{code-block} yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install markdown-pytest
      - run: pytest -v README.md
```

### With async support

```{code-block} yaml
- run: pip install "markdown-pytest[async]"
- run: pytest -v README.md
```

Add this to `pyproject.toml` so pytest-asyncio uses auto mode:

```{code-block} toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### With uv (faster installs)

```{code-block} yaml
- uses: astral-sh/setup-uv@v3
- run: uv run pytest -v README.md
```

Requires the project to be a `uv` project with markdown-pytest in the
dependencies.

## GitLab CI

```{code-block} yaml
# .gitlab-ci.yml
test-docs:
  image: python:3.12
  script:
    - pip install markdown-pytest
    - pytest -v README.md docs/
```

## Makefile target

Add a `make` target for local convenience that mirrors CI:

```{code-block} makefile
.PHONY: test-docs
test-docs:
	pytest -v README.md docs/
```

## Reporting

Use `--tb=short` in CI to get compact tracebacks:

```{code-block} bash
pytest -v --tb=short README.md
```

Use JUnit XML output for CI result dashboards:

```{code-block} bash
pytest -v --junitxml=results.xml README.md
```

In GitHub Actions, use the `dorny/test-reporter` action to display results
inline on the PR.

## Common CI gotchas

**Missing dependencies for documentation examples**

If your Markdown examples import a package that is not installed in the CI
environment, the test fails with `ModuleNotFoundError`. Either install the
package, or add `mark: skip(reason="requires X")` to that test.

**Async tests fail in CI but pass locally**

Ensure `asyncio_mode = "auto"` is set in `pyproject.toml` — some CI
environments do not inherit local settings files.

**Tests pass locally but fail in CI on Windows**

Path separator differences (`/` vs `\`) can cause failures. Use
`pathlib.Path` instead of string paths in your examples.

**Line endings on Windows**

GitHub Actions checks out files with `\r\n` on Windows by default. If your
Markdown tests contain shell commands or string comparisons that are
sensitive to line endings, add:

```{code-block} yaml
- uses: actions/checkout@v4
  with:
    eol: lf
```

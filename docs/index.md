# markdown-pytest

[![PyPI Version](https://img.shields.io/pypi/v/markdown-pytest.svg)](https://pypi.python.org/pypi/markdown-pytest/)
[![Python Versions](https://img.shields.io/pypi/pyversions/markdown-pytest.svg)](https://pypi.python.org/pypi/markdown-pytest/)
[![License](https://img.shields.io/pypi/l/markdown-pytest.svg)](https://pypi.python.org/pypi/markdown-pytest/)
[![Tests](https://github.com/mosquito/markdown-pytest/workflows/tests/badge.svg)](https://github.com/mosquito/markdown-pytest/actions)

**markdown-pytest** is a pytest plugin that collects and runs Python code
blocks directly from Markdown files, so your documentation examples are
always tested and never go stale.

```{code-block} text
$ pytest -v README.md

README.md::test_quick_start PASSED
README.md::test_example PASSED
README.md::test_with_tmp_path PASSED
```

## Why test your documentation?

Documentation examples rot. A library evolves, an API changes, someone
updates the code but forgets the README — and now your users copy-paste
broken examples. markdown-pytest solves this by running every Python code
block in your Markdown files as a real pytest test.

Because the test markers are plain HTML comments, rendered documentation
looks completely normal. Readers see clean code blocks; pytest sees a full
test suite.

## Features at a glance

- **Zero-config collection** — install and run `pytest docs/` or
  `pytest README.md`. No extra configuration needed.
- **Code splitting** — spread a single test across multiple code blocks,
  with prose in between, the way you would naturally write a tutorial.
- **Fixtures** — use `tmp_path`, `monkeypatch`, `capsys`, or any custom
  fixture from `conftest.py` directly in your Markdown code blocks.
- **Subtests** — run independent sub-cases sharing a common setup, powered
  by pytest's built-in subtests support (pytest 9+).
- **Hidden blocks** — hide setup or assertion code inside HTML comments so
  readers see only the interesting part.
- **Subprocess isolation** — run a block in a fresh Python process for
  tests that mutate global state or call `sys.exit()`.
- **Async support** — prefix a test name with `async ` to enable
  top-level `await` and async fixtures.
- **REPL / doctest mode** — write blocks in interactive Python shell
  format (`>>> ...`) and check their output.
- **Marks** — apply `xfail`, `skip`, or any custom mark directly from the
  comment.

## Quickstart

```{code-block} bash
pip install markdown-pytest
```

Add a comment above a Python code block in any `.md` file:

````{code-block} markdown
<!-- name: test_addition -->
```python
assert 1 + 1 == 2
```
````

Run:

```{code-block} bash
pytest README.md
```

That's it. Jump to the {doc}`tutorial/01_first_test` for a complete
walkthrough.

## Navigation

```{toctree}
:maxdepth: 2
:caption: Tutorials

tutorial/01_first_test
tutorial/02_split_blocks
tutorial/03_fixtures
tutorial/04_subtests
tutorial/05_hidden_blocks
tutorial/06_async
tutorial/07_subprocess
tutorial/08_doctest
```

```{toctree}
:maxdepth: 2
:caption: How-to guides

how-to/marks
how-to/conftest
how-to/ci
how-to/mixing_languages
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/comment_syntax
reference/configuration
reference/environments
```

```{toctree}
:maxdepth: 2
:caption: Explanation

explanation/how_it_works
```

# Tutorial 1 — Your first Markdown test

In this tutorial you will install markdown-pytest, write a Python code block
in a Markdown file, mark it as a test with an HTML comment, and run it with
pytest. The whole thing takes about five minutes.

## Prerequisites

- Python 3.10 or newer
- `pip` available in your shell

No prior pytest knowledge is required, although it helps to know what a
test function looks like.

## Step 1 — Install

```{code-block} bash
pip install markdown-pytest
```

That is all you need. The package registers itself as a pytest plugin via
the `pytest11` entry point, so pytest discovers it automatically — no
`conftest.py` or `pytest_plugins` declaration is needed.

To verify the installation:

```{code-block} bash
pytest --co -q README.md   # --co = collect only, -q = quiet
```

If markdown-pytest is installed and the file contains marked blocks, you
will see the test names listed. If the file has no marked blocks yet, the
output is empty — that is fine.

## Step 2 — Create a Markdown file

Create a file called `guide.md` in the root of your project (or open an
existing one).

The file can be anything — a README, a tutorial, API documentation, a
changelog. markdown-pytest ignores all content it does not recognise, so
you can add tests incrementally to files that already exist.

## Step 3 — Write a code block and mark it as a test

Paste the following into `guide.md`:

````{code-block} markdown
# My library

Here is a quick example:

<!-- name: test_addition -->
```python
result = 1 + 1
assert result == 2
```
````

The `<!-- name: test_addition -->` comment is the only thing markdown-pytest
needs. It tells the plugin:

- this block exists (not ignored)
- the test is named `test_addition`

The comment is invisible in rendered HTML — GitHub, MkDocs, Sphinx, and
every other Markdown renderer hide HTML comments from readers.

### Naming rules

The name must start with `test` by default (configurable, see
{doc}`../reference/configuration`). It follows the same conventions as a
Python function name: letters, digits, and underscores.

```{admonition} Valid names
:class: tip

`test_addition`, `test_parses_csv`, `test_edge_case_empty_list`
```

```{admonition} Invalid names — these are silently ignored
:class: warning

`addition` (no `test` prefix), `test addition` (space), `Test_Addition`
(uppercase T — treated as a different prefix)
```

## Step 4 — Run the test

```{code-block} bash
pytest guide.md
```

Expected output:

```{code-block} text
========================= test session starts ==========================
collected 1 item

guide.md::test_addition PASSED                                   [100%]

========================== 1 passed in 0.01s ===========================
```

Add `-v` for the verbose form that shows each test name on its own line:

```{code-block} bash
pytest -v guide.md
```

```{code-block} text
========================= test session starts ==========================
collected 1 item

guide.md::test_addition PASSED                                   [100%]

========================== 1 passed in 0.01s ===========================
```

## Step 5 — Make the test fail

Understanding failure output is as important as knowing how to pass.
Change the assertion:

````{code-block} markdown
<!-- name: test_addition -->
```python
result = 1 + 1
assert result == 3   # wrong on purpose
```
````

Run again:

```{code-block} bash
pytest guide.md
```

```{code-block} text
========================= test session starts ==========================
collected 1 item

guide.md::test_addition FAILED                                   [100%]

================================ FAILURES ==============================
_______________________ test_addition __________________________

guide.md:7: AssertionError

======================= short test summary info ========================
FAILED guide.md::test_addition - AssertionError
========================= 1 failed in 0.01s ============================
```

The traceback points directly to the line in `guide.md` — not to some
generated temp file. Fix the assertion back to `== 2` before continuing.

## Step 6 — Run all Markdown files at once

If your project has multiple Markdown files, point pytest at a directory:

```{code-block} bash
pytest docs/
```

Or mix Markdown with regular Python test files:

```{code-block} bash
pytest docs/ tests/
```

pytest collects `.md` and `.markdown` files automatically. Files without
any marked blocks are silently skipped.

## Step 7 — Add to CI

In GitHub Actions, add a step like:

```{code-block} yaml
- name: Test documentation examples
  run: pytest -v README.md docs/
```

Or extend an existing test step to include Markdown files alongside
`tests/`:

```{code-block} yaml
- name: Run tests
  run: pytest -v tests/ README.md
```

## What you learned

- Install markdown-pytest with a single `pip install`.
- Mark a Python code block by placing `<!-- name: test_... -->` directly
  above it.
- Run `pytest <file>.md` to execute the tests.
- Tracebacks reference the original Markdown line numbers.

## Next steps

A single block per test works well for short self-contained examples. For
longer examples with explanatory prose in between, see
{doc}`02_split_blocks` — it shows how to spread one test across several
code blocks.

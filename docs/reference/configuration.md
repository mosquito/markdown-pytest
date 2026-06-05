# Configuration reference

markdown-pytest adds one command-line option to pytest and respects the
standard pytest configuration files.

## `--md-prefix`

Controls which test names are collected from Markdown files.

**Default:** `test`

Only code blocks whose `name:` value starts with this prefix are collected.
Blocks with names that do not match the prefix are silently ignored.

### Command-line

```{code-block} bash
pytest --md-prefix=check README.md
```

With this setting, `<!-- name: check_addition -->` is collected and
`<!-- name: test_addition -->` is not.

### pyproject.toml

```{code-block} toml
[tool.pytest.ini_options]
addopts = "--md-prefix=check"
```

### pytest.ini

```{code-block} ini
[pytest]
addopts = --md-prefix=check
```

### setup.cfg

```{code-block} ini
[tool:pytest]
addopts = --md-prefix=check
```

## asyncio_mode

Not a markdown-pytest option, but required for async Markdown tests.

```{code-block} toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

Without this, pytest-asyncio does not run `async def` test functions
automatically. Since Markdown tests cannot be decorated with
`@pytest.mark.asyncio`, `auto` mode is required for async Markdown tests.

## Collected file extensions

Both `.md` and `.markdown` files are collected automatically via the
`pytest_collect_file` hook. No configuration is needed.

To restrict collection to a specific directory or file pattern, use pytest's
standard `testpaths` and `python_files` settings — though `python_files`
does not affect Markdown collection (it only controls `.py` files).

To collect Markdown files from a specific directory:

```{code-block} bash
pytest docs/
```

To exclude a directory:

```{code-block} bash
pytest --ignore=docs/drafts README.md docs/
```

## Markers

If you use custom `mark:` expressions in your Markdown comments, register
the markers to suppress pytest warnings:

```{code-block} toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "integration: requires external services",
]
```

## Full pyproject.toml example

```{code-block} toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = "-v --tb=short"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: requires real network or database",
]
```

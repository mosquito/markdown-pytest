# Supported environments

## Python versions

| Version | Status |
|---------|--------|
| 3.10 | Supported |
| 3.11 | Supported |
| 3.12 | Supported |
| 3.13 | Supported |
| 3.14 | Supported |
| PyPy 3.10+ | Supported |
| < 3.10 | Not supported |

The minimum version is Python 3.10 because the plugin uses
`str.removeprefix()` and structural pattern matching internally.

## pytest versions

| Version | Status |
|---------|--------|
| 9.0+ | Supported (subtests built-in) |
| < 9.0 | Not supported |

pytest 9.0 is the minimum version. It introduced built-in subtests support,
which markdown-pytest relies on for the `case:` feature.

## Operating systems

Tested on Linux, macOS, and Windows. Path handling uses `pathlib` throughout,
so cross-platform behaviour is consistent.

## Optional dependencies

### pytest-asyncio

Required for async tests (`name: async test_...`).

```{code-block} bash
pip install "markdown-pytest[async]"
# equivalent to:
pip install markdown-pytest pytest-asyncio
```

Compatible versions: `pytest-asyncio >= 1, < 2`.

### Other async plugins

Any pytest plugin that can run `async def` test functions works:

- `aiomisc-pytest`
- `anyio` (with `pytest-anyio`)
- Custom event loop plugins

Without an async plugin, async tests fail immediately with a clear error
message.

## File extensions collected

| Extension | Collected |
|-----------|-----------|
| `.md` | Yes |
| `.markdown` | Yes |
| `.rst` | No |
| `.txt` | No |

## Tracebacks

Tracebacks from failing tests preserve the original Markdown line numbers.
A failure in a code block at line 42 of `README.md` reports:

```{code-block} text
README.md:42: AssertionError
```

This works because the plugin compiles code with `filename=<path>` and
inserts blank lines to pad line numbers to match the Markdown source.

## pytest plugins compatibility

markdown-pytest is compatible with:

- `pytest-cov` (coverage)
- `pytest-xdist` (parallel execution)
- `pytest-timeout`
- `pytest-randomly`
- Any plugin that hooks into pytest's standard collection and execution.

## Entry point

The plugin registers itself via the `pytest11` entry point:

```{code-block} toml
[project.entry-points.pytest11]
markdown-pytest = "markdown_pytest"
```

No `conftest.py` import or `pytest_plugins` declaration is needed. Install
the package and pytest finds the plugin automatically.

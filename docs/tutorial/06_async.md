# Tutorial 6 — Async tests

If your library uses `asyncio` — coroutines, async context managers, async
generators — your documentation examples will too. markdown-pytest supports
top-level `await` in code blocks with a single prefix on the test name.

## Prerequisites

Completed {doc}`05_hidden_blocks`. Basic familiarity with Python's
`asyncio` module.

## Install the async extra

Async tests require a pytest plugin that manages the event loop.
`pytest-asyncio` is the most popular choice:

```{code-block} bash
pip install "markdown-pytest[async]"
```

This installs `pytest-asyncio`. You can use `aiomisc-pytest` or any other
compatible plugin instead.

Configure `pytest-asyncio` in `pyproject.toml`:

```{code-block} toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

Without `asyncio_mode = "auto"` you would need to mark every async test
with `@pytest.mark.asyncio` — but since Markdown tests are not Python
functions, the `auto` mode is required.

## Step 1 — Write an async test

Prefix the test name with `async ` (note the space):

````{code-block} markdown
<!-- name: async test_fetch -->
```python
import asyncio

async def fetch_value():
    await asyncio.sleep(0)   # simulate I/O
    return 42

result = await fetch_value()
assert result == 42
```
````

The `async ` prefix tells markdown-pytest to wrap the block in an
`async def` function so that top-level `await` is valid. pytest-asyncio
then runs it inside a managed event loop.

Run:

```{code-block} bash
pytest guide.md::test_fetch -v
```

```{code-block} text
guide.md::test_fetch PASSED
```

## Step 2 — Async with split blocks

When a test is split across multiple blocks, only **one** of them needs
the `async ` prefix — the whole test becomes async:

````{code-block} markdown
<!-- name: async test_pipeline -->
```python
import asyncio

async def step1():
    await asyncio.sleep(0)
    return [1, 2, 3]
```

<!-- name: test_pipeline -->
```python
items = await step1()
assert len(items) == 3
```
````

The second block has no `async ` prefix but it still uses `await` because
the overall test is async.

## Step 3 — Async fixtures

Async fixtures are supported. Define one in `conftest.py`:

```{code-block} python
# conftest.py
import pytest

@pytest.fixture
async def db_connection():
    # async setup
    conn = await create_connection()
    yield conn
    # async teardown
    await conn.close()
```

Request it in the usual way:

````{code-block} markdown
<!-- name: async test_db_query; fixtures: db_connection -->
```python
result = await db_connection.execute("SELECT 1")
assert result == 1
```
````

## Step 4 — Async with hidden blocks

Hidden blocks work the same way in async tests. Use a hidden setup block
to prepare async resources:

````{code-block} text
<!--
name: async test_async_stream
```python
import asyncio

async def make_stream(items):
    for item in items:
        await asyncio.sleep(0)
        yield item
```
-->
```python
results = []
async for value in make_stream([10, 20, 30]):
    results.append(value)
assert results == [10, 20, 30]
```
````

## Step 5 — Async with subtests

Async tests support `case:` blocks:

````{code-block} markdown
<!-- name: async test_async_cases -->
```python
import asyncio

async def double(x):
    await asyncio.sleep(0)
    return x * 2
```

<!-- name: async test_async_cases; case: small_number -->
```python
assert await double(3) == 6
```

<!-- name: async test_async_cases; case: zero -->
```python
assert await double(0) == 0
```

<!-- name: async test_async_cases; case: large_number -->
```python
assert await double(1000) == 2000
```
````

## Step 6 — Async subprocess mode

Adding `subprocess: true` to an async test runs the code in a child
process. The plugin automatically wraps the source in:

```{code-block} python
import asyncio

async def __amain():
    # your code here

asyncio.run(__amain())
```

````{code-block} markdown
<!-- name: async test_async_subprocess; subprocess: true -->
```python
import asyncio
await asyncio.sleep(0)
assert True
```
````

Subprocess mode does not require pytest-asyncio in the child process —
`asyncio.run()` manages the event loop directly.

## What happens without an event loop plugin

If you run an async test without pytest-asyncio (or a compatible plugin),
you get a clear error message listing the available options:

```{code-block} text
FAILED guide.md::test_fetch - RuntimeError: No async pytest plugin found.
Install one of: pytest-asyncio, aiomisc-pytest, anyio, ...
```

## What you learned

- Prefix the test name with `async ` to enable top-level `await`.
- Install `markdown-pytest[async]` for pytest-asyncio.
- Set `asyncio_mode = "auto"` in `pyproject.toml`.
- Only one block in a split test needs the `async ` prefix.
- Hidden blocks, subtests, and subprocess mode all work with async.

## Next steps

{doc}`07_subprocess` covers subprocess isolation — running a test in a
fresh Python process to test code that modifies global state or calls
`sys.exit()`.

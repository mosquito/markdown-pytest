# Tutorial 7 — Subprocess mode

Some code is hard to test safely in the same process as pytest:

- Code that calls `sys.exit()` or `os._exit()` would terminate pytest.
- Code that modifies `sys.modules`, `sys.path`, or other global state
  leaks between tests.
- Code that installs signal handlers or monkey-patches built-ins can
  interfere with pytest's own machinery.

Subprocess mode runs a test in a separate Python process so none of that
can happen.

## Prerequisites

Completed {doc}`06_async`. No additional packages needed.

## Step 1 — Add `subprocess: true`

````{code-block} markdown
<!-- name: test_isolated; subprocess: true -->
```python
import sys

# Pollute sys.modules — this cannot affect the pytest process
sys.modules["_fake_module_"] = object()
assert "_fake_module_" in sys.modules
```
````

Run:

```{code-block} bash
pytest guide.md::test_isolated -v
```

```{code-block} text
guide.md::test_isolated PASSED
```

The `sys.modules` mutation exists only in the child process and disappears
when it exits.

## Step 2 — How subprocess mode executes your code

When the plugin collects a subprocess test, it:

1. Concatenates the source code from all blocks with the same name.
2. Writes the source to a temporary `.py` file.
3. Runs `python <tempfile>` as a child process.
4. If the process exits with a non-zero code, the test fails and the
   standard error output is shown as the failure message.

The child process starts with a clean Python interpreter — no pytest, no
fixtures, no loaded plugins.

## Step 3 — Split blocks in subprocess mode

Multiple blocks with the same name and `subprocess: true` are combined
before being sent to the child process:

````{code-block} markdown
<!-- name: test_subprocess_split; subprocess: true -->
```python
def greet(name):
    return f"Hello, {name}!"
```

<!-- name: test_subprocess_split; subprocess: true -->
```python
assert greet("world") == "Hello, world!"
```
````

Both blocks must carry `subprocess: true`. The combined source runs in a
single subprocess.

## Step 4 — Hidden blocks with subprocess mode

Hidden setup blocks work the same way — they are hidden from readers but
included in the source sent to the child process:

````{code-block} text
<!--
name: test_subprocess_hidden;
subprocess: true
```python
EXPECTED = "success"
```
-->
```python
result = EXPECTED.upper()
assert result == "SUCCESS"
```
````

Readers see only the visible block. The hidden setup provides `EXPECTED`.

## Step 5 — Async subprocess mode

Prefix the name with `async ` to run async code in a subprocess. The
plugin wraps the source in `asyncio.run()` automatically:

````{code-block} markdown
<!-- name: async test_async_subprocess; subprocess: true -->
```python
import asyncio

async def work():
    await asyncio.sleep(0)
    return "done"

result = await work()
assert result == "done"
```
````

No event loop plugin is needed in subprocess mode — `asyncio.run()`
handles the event loop directly inside the child process.

## Step 6 — Checking exit codes

If the code under test calls `sys.exit(0)`, the test passes. Any non-zero
exit code fails the test. This is how you test CLI tools that call
`sys.exit()`:

````{code-block} markdown
<!-- name: test_exit_zero; subprocess: true -->
```python
import sys
sys.exit(0)
```
````

````{code-block} markdown
<!-- name: test_bad_exit; mark: xfail(strict=True); subprocess: true -->
```python
import sys
sys.exit(1)    # non-zero — test fails (and is expected to fail)
```
````

## Limitations

```{admonition} Fixtures are not available in subprocess mode
:class: warning

The child process does not run inside pytest, so `tmp_path`, `monkeypatch`,
and other fixtures are not available. If your test needs fixtures, omit
`subprocess: true`.
```

```{admonition} Subtests (case:) are not available in subprocess mode
:class: warning

`case:` blocks require the pytest `subtests` fixture, which is only
available inside the pytest process. Use separate subprocess tests instead.
```

```{admonition} Import path
:class: note

The child process inherits the parent's `sys.path`. If your project is
installed (or in the current directory), imports work normally. If you get
`ModuleNotFoundError`, make sure the package is installed in the same
environment.
```

## When to use subprocess mode

| Scenario | Use subprocess? |
|----------|----------------|
| Code calls `sys.exit()` | Yes |
| Code mutates `sys.modules` or `sys.path` | Yes |
| Code installs signal handlers | Yes |
| Normal function calls and assertions | No |
| Code that needs fixtures | No |
| Code that needs subtests | No |

## What you learned

- Add `subprocess: true` to run a block in a fresh Python process.
- Split blocks work in subprocess mode — all blocks must carry the flag.
- Hidden blocks are included in the subprocess source.
- Async code works in subprocess mode via `asyncio.run()`.
- Fixtures and subtests are not available in subprocess mode.

## Next steps

{doc}`08_doctest` covers the REPL / doctest mode — a way to write
interactive-shell-style examples that check printed output, the way
Python's own doctest module does.

# Tutorial 8 — REPL / doctest mode

The Python interactive shell format (`>>>` prompts, expected output on the
following lines) is widely recognised by developers. markdown-pytest can
run blocks written in this format using Python's built-in `doctest` module.

## Prerequisites

Completed {doc}`07_subprocess`. No additional packages are needed for sync
REPL tests.

## Step 1 — Write a REPL block

Add `repl: true` to the comment. Write the block as if you were typing
into a Python shell:

````{code-block} markdown
<!-- name: test_greet; repl: true -->
```python
>>> def greet(name):
...     return f"Hello, {name}!"
>>> greet("world")
'Hello, world!'
>>> print(greet("pytest"))
Hello, pytest!
```
````

Rules:
- Lines starting with `>>>` are executed.
- Lines starting with `...` are continuation lines (inside blocks or
  multi-line expressions).
- Lines without a prompt that immediately follow `>>>` or `...` lines are
  the **expected output**. The test fails if the actual output differs.
- Blank lines between `>>>` statements are fine — they do not end the
  block.

Run:

```{code-block} bash
pytest guide.md::test_greet -v
```

```{code-block} text
guide.md::test_greet PASSED
```

## Step 2 — Return values vs print output

`repr()` of a return value is shown automatically (just like in a real
shell). `print()` output appears as plain text without quotes.

````{code-block} markdown
<!-- name: test_output_types; repl: true -->
```python
>>> [1, 2, 3]
[1, 2, 3]
>>> print("hello")
hello
>>> 42
42
>>> x = 10
>>> x
10
```
````

When a statement produces no return value (assignment, `import`, `for`
loops), nothing is expected on the next line.

## Step 3 — Standard doctest directives

All `# doctest: +DIRECTIVE` flags work:

````{code-block} markdown
<!-- name: test_ellipsis; repl: true -->
```python
>>> [1, 2, 3, 4, 5]  # doctest: +ELLIPSIS
[1, 2, ...]
>>> "hello world"   # doctest: +NORMALIZE_WHITESPACE
'hello  world'
```
````

Useful directives:

| Directive | What it does |
|-----------|-------------|
| `+ELLIPSIS` | `...` in expected output matches anything |
| `+NORMALIZE_WHITESPACE` | Any run of whitespace matches any other |
| `+SKIP` | Skip this specific example |
| `+IGNORE_EXCEPTION_DETAIL` | Match exception type but not message |

## Step 4 — Expecting exceptions

Write the exception type and message as it would appear in the shell:

````{code-block} markdown
<!-- name: test_exception; repl: true -->
```python
>>> 1 / 0
Traceback (most recent call last):
    ...
ZeroDivisionError: division by zero
```
````

The `Traceback (most recent call last):` header and `...` on the next line
are required by the doctest format. The module path in the exception
message is optional — doctest matches only the last line by default.

## Step 5 — Split REPL blocks

Multiple blocks with the same name share a session — variables defined in
an earlier block are available in later ones:

````{code-block} markdown
<!-- name: test_session; repl: true -->
```python
>>> items = [1, 2, 3]
>>> len(items)
3
```

Add an item and verify:

<!-- name: test_session; repl: true -->
```python
>>> items.append(4)
>>> items
[1, 2, 3, 4]
```
````

Both blocks carry `repl: true`. The session (namespace) is preserved
across them — `items` is available in the second block.

## Step 6 — Async REPL

Prefix the name with `async ` to enable top-level `await` inside REPL
blocks:

````{code-block} markdown
<!-- name: async test_async_repl; repl: true -->
```python
>>> import asyncio
>>> async def fetch():
...     await asyncio.sleep(0)
...     return 42
>>> await fetch()
42
```
````

Requires an async pytest plugin (same as regular async tests — see
{doc}`06_async`).

State is preserved across split async REPL blocks within the same event
loop session.

## When to use REPL mode vs regular mode

| Situation | Use |
|-----------|-----|
| Checking printed output inline | `repl: true` |
| Showing interactive exploration | `repl: true` |
| Running a sequence of statements | regular |
| Using fixtures | regular |
| Using subtests | regular |

REPL mode cannot use fixtures or `case:` subtests. If you need those
features, use a regular block with explicit `assert` statements.

## Common mistakes

**Missing `...` continuation lines**

Multi-line `>>>` statements require `...` on continuation lines:

```{code-block} python
>>> def f(x):
...     return x + 1   # correct
>>> def f(x):
    return x + 1       # SyntaxError — missing ...
```

**Expected output on wrong line**

The expected output must appear on the line **immediately** after the
`>>>` or `...` block. A blank line ends the expected output and starts a
new statement.

**`repl: true` on only one block of a split pair**

All blocks in a split REPL test must carry `repl: true`. If one block
lacks it, that block is treated as a regular test block instead of a
doctest block.

## What you learned

- Add `repl: true` to run a block as a Python interactive-shell session.
- `>>>` lines are code; following lines without a prompt are expected
  output.
- All standard `# doctest: +DIRECTIVE` flags are supported.
- Split REPL blocks share a session across the same name.
- Prefix the name with `async ` for top-level `await` in REPL blocks.

---

You have now completed all eight tutorials. For task-specific guidance,
move on to the **How-to guides**.

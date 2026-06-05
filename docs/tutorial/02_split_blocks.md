# Tutorial 2 — Splitting a test across multiple blocks

Good documentation tells a story. You introduce a concept, show a snippet,
explain what happened, then build on it with another snippet. But a pytest
test is one continuous unit — the second block needs the variables defined
in the first.

markdown-pytest solves this with **code splitting**: give several blocks
the same `name` and they are merged into a single test at collection time,
in document order.

## Prerequisites

Completed {doc}`01_first_test`. You have `guide.md` and markdown-pytest
installed.

## The problem without splitting

Suppose you want to document `itertools.chain` in two steps:

1. First block: import and explain the function.
2. Second block: demonstrate it.

Without splitting, each block would be its own independent test. The second
block would fail because `chain` is not imported there.

## Step 1 — Write two blocks with the same name

In `guide.md`, write:

````{code-block} markdown
## Using itertools.chain

Import the function first:

<!-- name: test_chain_demo -->
```python
from itertools import chain
```

`chain` concatenates iterables without copying them:

<!-- name: test_chain_demo -->
```python
result = list(chain([1, 2], [3, 4]))
assert result == [1, 2, 3, 4]
```
````

Both blocks have `name: test_chain_demo`. markdown-pytest sees them as two
parts of one test. When the test runs, it executes:

```{code-block} python
from itertools import chain
# (prose in between is ignored)
result = list(chain([1, 2], [3, 4]))
assert result == [1, 2, 3, 4]
```

Run it:

```{code-block} bash
pytest guide.md -v
```

```{code-block} text
guide.md::test_chain_demo PASSED
```

## Step 2 — Add prose between blocks

The prose between the two blocks does not affect execution. You can write as
much explanatory text as you like — it is stripped out during collection.
Only the Python code blocks with the matching name are combined.

For example:

````{code-block} markdown
## Building a pipeline

Start with a list of numbers:

<!-- name: test_pipeline -->
```python
numbers = [1, 2, 3, 4, 5]
```

Filter to even numbers only. Python's built-in `filter` returns an
iterator, so we wrap it in `list()` to materialise the result:

<!-- name: test_pipeline -->
```python
evens = list(filter(lambda x: x % 2 == 0, numbers))
```

Square each even number using a list comprehension:

<!-- name: test_pipeline -->
```python
squared = [x ** 2 for x in evens]
assert squared == [4, 16]
```
````

Three blocks, one test, prose between each one.

## Step 3 — Non-consecutive blocks

Split blocks do not need to be adjacent. A completely different test can
appear between two blocks that share a name:

````{code-block} markdown
<!-- name: test_a -->
```python
x = 10
```

<!-- name: test_unrelated -->
```python
assert True
```

<!-- name: test_a -->
```python
assert x == 10   # x is from the first block — this works
```
````

The plugin collects all blocks named `test_a` regardless of what appears
between them. `test_unrelated` becomes its own separate test.

## Step 4 — Fixtures in split blocks

When using fixtures, only the **first** block needs the `fixtures:`
declaration. All subsequent blocks with the same name automatically share
the same namespace, including the fixture variables:

````{code-block} markdown
<!-- name: test_file_pipeline; fixtures: tmp_path -->
```python
src = tmp_path / "input.txt"
src.write_text("hello\nworld\n")
```

Read and process the file in a second block — `tmp_path` and `src` are
still in scope:

<!-- name: test_file_pipeline -->
```python
lines = src.read_text().splitlines()
assert len(lines) == 2
assert lines[0] == "hello"
```
````

See {doc}`03_fixtures` for the full guide on fixtures.

## How it works internally

At collection time the plugin reads the whole file and groups blocks by
name. For each name it sorts the blocks by their line number and
concatenates the source lines. Line numbers are preserved — if block 1 is
at line 10 and block 2 is at line 30, the compiled source has blank lines
filling lines 11–29 so that tracebacks still point to the right location
in the original file.

## Common mistakes

**Using different names by accident**

If you accidentally write `test_Chain_demo` (capital C) for the second
block, it becomes a separate test that will fail because `chain` is not
imported.

```{admonition} Tip
:class: tip

Paste names from the first block — don't retype them. A typo creates a
silent second test that imports nothing.
```

**Expecting ordering across files**

Split blocks are combined only within a single file. Two blocks named
`test_foo` in two different `.md` files are two separate tests, not one.

## What you learned

- Give two or more blocks the same `name` and they run as one test.
- Blocks can be separated by any amount of prose.
- Blocks do not need to be adjacent — other tests can appear in between.
- Only the first block needs the `fixtures:` declaration.

## Next steps

{doc}`03_fixtures` shows every way to inject pytest fixtures into your
Markdown tests — from simple `tmp_path` usage to multiple fixtures,
multiline declarations, and mixing fixtures across split blocks.

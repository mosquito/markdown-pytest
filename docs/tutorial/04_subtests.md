# Tutorial 4 — Subtests

A subtest is an independent mini-test that shares setup with its siblings.
If one subtest fails, the others still run — unlike a single test where the
first failure stops execution. This is perfect for documenting a function
with many different inputs side by side.

pytest 9.0 ships subtests as a built-in feature. No extra packages are
needed.

## Prerequisites

Completed {doc}`03_fixtures`. You should know how split blocks work.

## The problem without subtests

Suppose you want to document three edge cases for a string sanitiser:

````{code-block} markdown
<!-- name: test_sanitise_empty -->
```python
from mylib import sanitise
assert sanitise("") == ""
```

<!-- name: test_sanitise_spaces -->
```python
from mylib import sanitise       # imported again
assert sanitise("  hello  ") == "hello"
```

<!-- name: test_sanitise_special -->
```python
from mylib import sanitise       # imported again
assert sanitise("a<b>c") == "abc"
```
````

Three separate tests — three imports. If `sanitise` needs expensive
setup, you repeat it three times. With subtests you set up once and vary
the assertion:

## Step 1 — Add `case:` to each variation

The first block (no `case:`) is the **shared setup**. Each subsequent block
with a `case:` key is an independent subtest.

````{code-block} markdown
<!-- name: test_sanitise -->
```python
def sanitise(s):
    return s.strip().replace("<", "").replace(">", "")
```

<!-- name: test_sanitise; case: empty_string -->
```python
assert sanitise("") == ""
```

<!-- name: test_sanitise; case: strips_whitespace -->
```python
assert sanitise("  hello  ") == "hello"
```

<!-- name: test_sanitise; case: removes_angle_brackets -->
```python
assert sanitise("a<b>c") == "abc"
```
````

When run:

```{code-block} bash
pytest guide.md -v
```

```{code-block} text
guide.md::test_sanitise PASSED
  test_sanitise/empty_string PASSED
  test_sanitise/strips_whitespace PASSED
  test_sanitise/removes_angle_brackets PASSED
```

Three sub-results, one test entry in the summary.

## Step 2 — One failure does not stop the rest

Change the second case to a wrong expected value:

````{code-block} markdown
<!-- name: test_sanitise; case: strips_whitespace -->
```python
assert sanitise("  hello  ") == "HELLO"   # wrong
```
````

Run again:

```{code-block} text
guide.md::test_sanitise FAILED
  test_sanitise/empty_string PASSED
  test_sanitise/strips_whitespace FAILED
  test_sanitise/removes_angle_brackets PASSED
```

`strips_whitespace` failed, but `removes_angle_brackets` still ran and
passed. Without subtests, execution would have stopped at the first failure.

Fix the assertion before continuing.

## Step 3 — Add fixtures to subtests

Fixtures work the same way as with regular split blocks. Declare them on
the setup block (no `case:`); they are available in all case blocks:

````{code-block} markdown
<!-- name: test_file_cases; fixtures: tmp_path -->
```python
base = tmp_path / "data"
base.mkdir()
```

<!-- name: test_file_cases; case: file_creation -->
```python
f = base / "a.txt"
f.write_text("hello")
assert f.exists()
```

<!-- name: test_file_cases; case: file_content -->
```python
f = base / "a.txt"
f.write_text("hello")
assert f.read_text() == "hello"
```
````

`tmp_path` is requested once and shared across all cases. Each case
receives its own fresh `tmp_path` value because pytest re-runs the
function-scoped fixture for each subtest.

## Step 4 — Prose between case blocks

You can add explanatory text between `case:` blocks just like with regular
split blocks:

````{code-block} markdown
<!-- name: test_counter -->
```python
from collections import Counter
c = Counter()
```

Start by verifying the counter starts at zero:

<!-- name: test_counter; case: initial_value -->
```python
assert c["missing_key"] == 0
```

Increment a key and check it:

<!-- name: test_counter; case: after_increment -->
```python
c["x"] += 1
assert c["x"] == 1
```

Multiple increments accumulate:

<!-- name: test_counter; case: accumulation -->
```python
c["x"] += 1
c["x"] += 1
assert c["x"] == 2
```
````

The prose between blocks is documentation — it is stripped during
collection.

## Step 5 — Case names in output

Case names appear in the test output and in failure messages. Choose names
that describe the scenario, not the implementation:

```{admonition} Good case names
:class: tip

`case: empty_input`, `case: negative_number`, `case: unicode_string`,
`case: max_value`
```

```{admonition} Unhelpful case names
:class: warning

`case: test1`, `case: case_a`, `case: foo`
```

Spaces are allowed in case names: `case: strips leading spaces` — they
appear as-is in output.

## How subtests work internally

When the plugin collects a test with `case:` blocks, it wraps each case in
a `with subtests.test(msg='...')` context manager. The `subtests` fixture
is automatically added to the test's fixture list. If a case raises an
exception, the context manager catches it, records the failure, and
execution continues with the next case.

## Common mistakes

**Forgetting the setup block**

If every block has a `case:`, there is no shared setup. Each case gets its
own fresh namespace — variables defined in one case are not visible in
others. Add one block without `case:` to define shared state.

**Setup block also has `case:`**

The block without `case:` is the setup. If you accidentally add `case:` to
the setup block, it becomes a case and there is no shared setup.

**Expecting a `subtests` import**

You do not need to import anything. The `subtests` fixture is injected
automatically by the plugin.

## What you learned

- Add `case: name` to mark a block as a subtest.
- The block without `case:` is the shared setup.
- All cases run even when one fails.
- Fixtures are available in all case blocks.

## Next steps

{doc}`05_hidden_blocks` covers how to write documentation that looks
polished to readers — with setup and assertions hidden in HTML comments —
while still being fully tested.

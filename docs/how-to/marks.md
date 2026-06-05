# How to use pytest marks

pytest marks let you attach metadata to tests — skip them, mark them as
expected failures, or tag them for selective runs. markdown-pytest supports
the full marks system via the `mark:` key in the HTML comment.

## Basic syntax

```{code-block} markdown
<!-- name: test_name; mark: <expression> -->
```

The expression is evaluated as `pytest.mark.<expression>`. Everything after
`mark:` is passed directly to pytest's mark machinery.

## Skip a test

```{code-block} markdown
<!-- name: test_needs_network; mark: skip(reason="requires network access") -->
```

The test is collected but skipped. It appears as `s` in the summary:

```{code-block} text
guide.md::test_needs_network SKIPPED (requires network access)
```

### Conditional skip

Use `skipif` to skip based on a runtime condition:

```{code-block} markdown
<!-- name: test_unix_only; mark: skipif(sys.platform == "win32", reason="POSIX only") -->
```

Note: the expression is evaluated at collection time, so `sys` must be
importable without additional setup (it always is).

## Mark a test as expected to fail

`xfail` marks a test that is known to fail. It passes (as `x`) if it
fails, and surprises (as `X`) if it unexpectedly passes.

```{code-block} markdown
<!-- name: test_known_bug; mark: xfail(reason="issue #42, not fixed yet") -->
```

### Expected failure with a specific exception

```{code-block} markdown
<!-- name: test_divide_by_zero; mark: xfail(raises=ZeroDivisionError) -->
```python
1 / 0
```
```

If the block raises `ZeroDivisionError`, the test is marked `xfail` (as
expected). If it raises a different exception, the test fails.

### Strict xfail

`strict=True` turns an unexpected pass into a test failure:

```{code-block} markdown
<!-- name: test_strict_xfail; mark: xfail(strict=True, reason="must fail") -->
```

Use this when a test _must_ fail — an unexpected pass means the bug was
fixed and the mark should be removed.

## Apply multiple marks

Use semicolons to add more metadata keys, but each test supports only one
`mark:` value. To apply multiple marks, use comma-separated `mark.` calls
in a single expression — or use a custom mark:

```{code-block} markdown
<!-- name: test_slow_network; mark: xfail(reason="slow"); mark: skip(reason="no network") -->
```

When `mark:` appears multiple times, the values are merged — both marks
are applied.

## Marks with split blocks

Only the **first** block needs the `mark:` declaration. Subsequent blocks
with the same name inherit the mark:

```{code-block} markdown
<!-- name: test_marked_split; mark: xfail -->
```python
x = 1
```

<!-- name: test_marked_split -->
```python
assert x == 2   # fails — expected
```
```

## Custom marks

Register your custom marks in `pyproject.toml`:

```{code-block} toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: requires external services",
]
```

Then use them in Markdown:

```{code-block} markdown
<!-- name: test_heavy; mark: slow -->
```python
import time
time.sleep(0.001)
assert True
```
```

Run only fast tests:

```{code-block} bash
pytest guide.md -m "not slow"
```

## Selecting tests by mark

All standard `-m` expressions work:

```{code-block} bash
pytest guide.md -m "not slow"
pytest guide.md -m "integration or smoke"
pytest guide.md -m "xfail"
```

## Reference

See the full list of built-in marks in the
[pytest marks documentation](https://docs.pytest.org/en/stable/how-to/mark.html).

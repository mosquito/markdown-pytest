# Tutorial 3 — Using fixtures

pytest fixtures provide reusable, isolated resources to tests — temporary
directories, captured output, environment variable overrides, and anything
you define yourself. markdown-pytest gives you full access to the same
fixture system from inside Markdown code blocks.

## Prerequisites

Completed {doc}`02_split_blocks`. Familiarity with at least one pytest
fixture (`tmp_path` is the most common).

## Declaring fixtures

Add `fixtures: <name>` to the HTML comment. The fixture is then available
as a variable with that exact name inside the code block.

````{code-block} markdown
<!-- name: test_tmp_file; fixtures: tmp_path -->
```python
p = tmp_path / "hello.txt"
p.write_text("hello")
assert p.read_text() == "hello"
```
````

`tmp_path` is a built-in pytest fixture that provides a temporary directory
unique to the test invocation. It is cleaned up automatically after the
test.

## Step 1 — Single fixture

The simplest case: one fixture, one block.

````{code-block} markdown
<!-- name: test_write_file; fixtures: tmp_path -->
```python
path = tmp_path / "data.txt"
path.write_text("content")
assert path.exists()
assert path.read_text() == "content"
```
````

Run:

```{code-block} bash
pytest guide.md::test_write_file -v
```

```{code-block} text
guide.md::test_write_file PASSED
```

## Step 2 — Multiple fixtures

List fixtures separated by commas:

````{code-block} markdown
<!-- name: test_env_and_file; fixtures: tmp_path, monkeypatch -->
```python
import os
monkeypatch.setenv("DATA_DIR", str(tmp_path))
assert os.environ["DATA_DIR"] == str(tmp_path)
```
````

`monkeypatch` lets you set environment variables (and much more) safely —
changes are automatically undone after the test.

## Step 3 — Multiline fixture declarations

If the fixture list is long, break it across lines inside the comment:

````{code-block} markdown
<!--
    name: test_multi;
    fixtures: tmp_path,
              monkeypatch,
              capsys
-->
```python
import os
monkeypatch.setenv("X", "1")
print(os.environ["X"])
captured = capsys.readouterr()
assert captured.out.strip() == "1"
```
````

The indentation inside the comment is ignored; only the values matter.

## Step 4 — Fixtures declared on separate lines

Alternatively, use a separate `fixtures:` key for each fixture:

````{code-block} markdown
<!--
    name: test_separate;
    fixtures: tmp_path;
    fixtures: capsys
-->
```python
(tmp_path / "f.txt").write_text("hi")
print("hi")
captured = capsys.readouterr()
assert captured.out.strip() == "hi"
```
````

Duplicate keys are merged automatically — this is equivalent to listing
them all on one line.

## Step 5 — Fixtures across split blocks

When a test is split into multiple blocks, declare fixtures only in the
**first** block. All blocks with the same name share the same namespace,
so fixtures are available everywhere:

````{code-block} markdown
<!-- name: test_split_file; fixtures: tmp_path -->
```python
path = tmp_path / "log.txt"
path.write_text("line1\nline2\n")
```

Now read the file back:

<!-- name: test_split_file -->
```python
lines = path.read_text().splitlines()
assert lines == ["line1", "line2"]
```
````

The second block does not repeat `fixtures: tmp_path`. `tmp_path` and
`path` are both in scope because all blocks share one namespace.

## Step 6 — Fixtures from different blocks merged

You can declare different fixtures in different blocks — they are all
requested and injected into the shared namespace:

````{code-block} markdown
<!-- name: test_merged; fixtures: tmp_path -->
```python
p = tmp_path / "out.txt"
p.write_text("merged")
```

<!-- name: test_merged; fixtures: capsys -->
```python
print(p.read_text())
captured = capsys.readouterr()
assert captured.out.strip() == "merged"
```
````

Both `tmp_path` and `capsys` are requested even though they appear in
separate blocks.

## Step 7 — Custom fixtures from conftest.py

Any fixture defined in `conftest.py` works exactly the same way. Create
`conftest.py` next to your Markdown file (or anywhere pytest can find it):

```{code-block} python
# conftest.py
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value", "count": 42}
```

Use it in a Markdown block:

````{code-block} markdown
<!-- name: test_custom_fixture; fixtures: sample_data -->
```python
assert sample_data["key"] == "value"
assert sample_data["count"] == 42
```
````

See {doc}`../how-to/conftest` for patterns with `autouse` fixtures,
factories, and session-scoped setup.

## Common built-in fixtures

| Fixture | What it provides |
|---------|-----------------|
| `tmp_path` | Temporary `pathlib.Path` directory, unique per test |
| `tmp_path_factory` | Factory for creating multiple temp directories |
| `monkeypatch` | Patch objects, env vars, and sys.path safely |
| `capsys` | Capture `sys.stdout` and `sys.stderr` |
| `capfd` | Capture file descriptors 1 and 2 |
| `caplog` | Capture log records |
| `request` | Access test metadata (name, module, config) |

Any of these can be listed in the `fixtures:` declaration.

## Common mistakes

**Declaring fixtures in every block**

Only the first block needs `fixtures:`. If you repeat the declaration in
later blocks, the fixture is requested twice — usually harmless but
redundant.

**Typo in fixture name**

If you write `fixtures: tmp_paths` (extra `s`), pytest raises
`FixtureLookupError` because no fixture with that name exists. The error
message lists similar names.

**Scope mismatch**

A session-scoped fixture cannot depend on a function-scoped fixture. This
constraint comes from pytest itself and applies equally to Markdown tests.

## What you learned

- Add `fixtures: name` to inject any pytest fixture.
- Comma-separate multiple fixtures, or use separate `fixtures:` keys.
- Only the first split block needs the `fixtures:` declaration.
- Custom fixtures from `conftest.py` work without any special setup.

## Next steps

{doc}`04_subtests` shows how to run many independent variations of a test
that all share the same setup — without duplicating the setup code.

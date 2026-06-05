# Comment syntax reference

The HTML comment placed above (or around) a Python code block is the only
configuration interface for markdown-pytest. This page documents every
parameter and every valid syntax variant.

## Basic structure

```{code-block} text
<!-- key1: value1; key2: value2 -->
```

- Key-value pairs are separated by semicolons (`;`).
- The trailing semicolon after the last pair is optional.
- Whitespace around keys and values is stripped.
- Comments can span multiple lines.

## Parameters

### `name` (required)

The test identifier. Must be unique per file (within a given name,
all blocks are merged into one test).

```{code-block} text
<!-- name: test_my_feature -->
```

**Rules:**

- Must start with the configured prefix (`test` by default — see
  {doc}`configuration`).
- Must be a valid Python identifier: letters, digits, and underscores.
  No spaces (spaces before the prefix `async ` are the only exception).
- Case-sensitive: `test_foo` and `test_Foo` are two different tests.

**Async prefix:**

Prefix the name with `async ` to enable top-level `await`:

```{code-block} text
<!-- name: async test_my_async_feature -->
```

The `async ` part is stripped from the collected test name — the test
is named `test_my_async_feature` in pytest output.

### `case`

Marks a block as a subtest. The first block with a given name and no
`case:` key is the shared setup; each `case:` block is an independent
subtest that runs after the setup.

```{code-block} text
<!-- name: test_foo; case: my_scenario -->
```

- Case names can contain spaces: `case: handles empty input`.
- If all blocks have `case:`, there is no shared setup — each case
  runs in its own fresh namespace.
- Subtests require pytest 9.0+.

### `fixtures`

Comma-separated list of pytest fixture names to inject as variables.

```{code-block} text
<!-- name: test_foo; fixtures: tmp_path, monkeypatch, capsys -->
```

The fixture values are available as variables with the same names inside
the code block.

**Multiline form:**

```{code-block} text
<!--
    name: test_foo;
    fixtures: tmp_path,
              monkeypatch,
              capsys
-->
```

**Multiple `fixtures:` keys:**

```{code-block} text
<!--
    name: test_foo;
    fixtures: tmp_path;
    fixtures: monkeypatch
-->
```

Duplicate keys are merged — the two forms above are equivalent.

**Only the first block needs `fixtures:`** when a test is split across
multiple blocks. Later blocks share the same namespace.

### `subprocess`

Set to `true` to run the test in a separate Python process.

```{code-block} text
<!-- name: test_isolated; subprocess: true -->
```

- Fixtures and `case:` subtests are not available in subprocess mode.
- Async code is wrapped in `asyncio.run()` automatically.
- The child process inherits the parent's `sys.path`.
- A non-zero exit code fails the test.

### `repl`

Set to `true` to run the block as a doctest (interactive shell session).

```{code-block} text
<!-- name: test_session; repl: true -->
```

- Lines starting with `>>>` are executed.
- Lines starting with `...` are continuation lines.
- Following lines without a prompt are expected output.
- All standard `# doctest: +DIRECTIVE` flags are supported.
- Cannot be combined with `subprocess: true`.

### `mark`

A pytest mark expression, evaluated as `pytest.mark.<expression>`.

```{code-block} text
<!-- name: test_foo; mark: xfail(raises=ValueError) -->
<!-- name: test_bar; mark: skip(reason="not implemented") -->
<!-- name: test_baz; mark: skipif(sys.platform == "win32", reason="POSIX only") -->
```

Multiple `mark:` keys are merged — all marks are applied:

```{code-block} text
<!--
    name: test_multi;
    mark: xfail;
    mark: slow
-->
```

## Comment delimiters

Both two-dash and three-dash variants are recognised. All four forms are
equivalent:

```{code-block} text
<!--  name: test_foo -->
<!--- name: test_foo --->
<!--  name: test_foo --->
<!--- name: test_foo -->
```

## Hidden block syntax

A code block placed **inside** the comment is hidden from rendered
Markdown but executed as part of the test. The metadata keys come first,
then the code fence:

```{code-block} text
<!--
name: test_foo;
fixtures: tmp_path
```python
p = tmp_path / "f.txt"
```
-->
```

The closing `-->` appears **after** the closing ` ``` `. The opening
` ```python ` and closing ` ``` ` are part of the comment.

## Full example

A test with all parameters used together:

```{code-block} text
<!--
    name: async test_full_example;
    fixtures: tmp_path, monkeypatch;
    mark: xfail(strict=False, reason="experimental")
    ```python
    # hidden setup block
    import json
    path = tmp_path / "data.json"
    ```
-->
```python
# visible block — readers see this
path.write_text(json.dumps({"key": "value"}))
```
<!--
name: async test_full_example
```python
# hidden assertions
data = json.loads(path.read_text())
assert data["key"] == "value"
```
-->
```

## Ignored blocks

A Python block is **silently ignored** when:

- It has no comment above (or around) it.
- The comment has no `name:` key.
- The `name:` value does not start with the configured prefix.
- The block uses a language tag other than `python`.
- The block uses a non-triple backtick fence.

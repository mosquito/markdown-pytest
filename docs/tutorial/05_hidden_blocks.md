# Tutorial 5 — Hidden code blocks

The best documentation examples focus on one concept at a time. But tests
need setup, teardown, and assertions that would clutter a documentation
example. Hidden blocks solve this: you put the boilerplate inside an HTML
comment so readers never see it, but the plugin runs it.

## Prerequisites

Completed {doc}`04_subtests`. You understand split blocks and fixtures.

## The idea

An HTML comment in Markdown hides its content from all renderers. If you
put a Python code block inside the comment, readers do not see it — but
markdown-pytest parses inside comments and runs the code.

## Variant 1 — Hidden setup before a visible block

The most common pattern: hidden imports and setup, visible demo code.

In the raw Markdown source you write:

````{code-block} text
<!--
name: test_csv_demo;
fixtures: tmp_path
```python
import csv, io
csv_file = tmp_path / "data.csv"
csv_file.write_text("name,score\nAlice,95\nBob,87\n")
```
-->
```python
rows = []
with open(csv_file) as f:
    for row in csv.DictReader(f):
        rows.append(row)
```
````

What readers see when the Markdown is rendered:

```{code-block} python
rows = []
with open(csv_file) as f:
    for row in csv.DictReader(f):
        rows.append(row)
```

Clean, focused, no boilerplate. But the test runs the hidden block first,
so `csv_file` exists when the visible block runs.

## Variant 2 — Hidden assertions after a visible block

Use split blocks with a hidden second block to add assertions that readers
do not need to see:

````{code-block} text
<!-- name: test_csv_demo -->
```python
rows = []
with open(csv_file) as f:
    for row in csv.DictReader(f):
        rows.append(row)
```
<!--
name: test_csv_demo
```python
assert len(rows) == 2
assert rows[0] == {"name": "Alice", "score": "95"}
```
-->
````

Readers see only the `for` loop. The assertions are hidden but still run.

## Step 1 — The complete polished pattern

Combine both variants: hidden setup before, visible demo, hidden
assertions after. This is the recommended pattern for tutorial-style
documentation.

In the raw Markdown:

````{code-block} text
<!--
name: test_json_roundtrip;
fixtures: tmp_path
```python
import json
path = tmp_path / "config.json"
```
-->

Write a config file:

```python
config = {"debug": True, "workers": 4}
path.write_text(json.dumps(config))
```

Read it back:

```python
loaded = json.loads(path.read_text())
assert loaded == config
```
<!--
name: test_json_roundtrip
```python
assert loaded["debug"] is True
assert loaded["workers"] == 4
```
-->
````

Readers see two code blocks — write and read — with prose between them.
They look like a natural tutorial. The hidden blocks take care of imports,
file setup, and final assertions.

The blocks with the same name (`test_json_roundtrip`) are combined in
document order:

1. Hidden setup block (imports, `path`)
2. Visible "write" block
3. Visible "read" block
4. Hidden assertion block

## Step 2 — Try it yourself

Create `guide.md` with this content (copy the raw text including the HTML
comments — not the rendered version above):

````{code-block} text
## JSON round-trip

<!--
name: test_json_roundtrip;
fixtures: tmp_path
```python
import json
path = tmp_path / "config.json"
```
-->
```python
config = {"debug": True, "workers": 4}
path.write_text(json.dumps(config))
loaded = json.loads(path.read_text())
```
<!--
name: test_json_roundtrip
```python
assert loaded == config
```
-->
````

Run:

```{code-block} bash
pytest guide.md -v
```

```{code-block} text
guide.md::test_json_roundtrip PASSED
```

View the rendered result in any Markdown viewer — only the `config =...`
block is visible.

## Step 3 — Hidden block syntax rules

The hidden block is a code block placed **inside** an HTML comment that
also contains the `name:` metadata:

```{code-block} text
<!--
name: test_foo
```python
# this code runs but is hidden from readers
x = 1
```
-->
```

Note that the closing `-->` is on its own line **after** the closing
` ``` `. The opening ` ```python ` and closing ` ``` ` are inside the
comment.

The comment can also carry other metadata. Put the metadata keys first,
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

## Step 4 — Multiple hidden blocks

You can have more than one hidden block per test. They run in document
order along with the visible blocks:

````{code-block} text
<!--
name: test_multi_hidden;
fixtures: tmp_path
```python
import json
path = tmp_path / "x.json"
```
-->
```python
path.write_text(json.dumps({"a": 1}))
```
<!--
name: test_multi_hidden
```python
assert json.loads(path.read_text()) == {"a": 1}
```
-->
<!--
name: test_multi_hidden
```python
assert path.exists()
```
-->
````

## Debugging hidden blocks

Because hidden blocks are inside HTML comments, they do not show in
rendered Markdown. If a test fails and you are not sure which hidden block
is the problem, view the raw Markdown source and look for comments that
contain code fences.

The traceback always includes a line number pointing to the original
Markdown file — you can jump straight to that line to find the relevant
block.

## What you learned

- Place a code block inside an HTML comment to hide it from readers.
- Hidden blocks run in document order with visible blocks.
- The recommended pattern: hidden setup → visible demo → hidden assertions.
- The hidden block's comment must contain the `name:` key and a code fence.

## Next steps

{doc}`06_async` shows how to test async code — functions that use
`await` — with just an `async ` prefix on the test name.

# How markdown-pytest works

This page explains the internals of markdown-pytest — how it finds tests,
what it does with them, and why certain design decisions were made.

## The collection phase

pytest's collection phase discovers test items. markdown-pytest hooks into
it via two standard plugin hooks:

- `pytest_collect_file` — called for every file pytest encounters. The
  plugin returns a `MarkdownFile` collector when the file extension is
  `.md` or `.markdown`.
- `pytest_collect_item` — the collector's `collect()` method is called to
  produce test items.

### Parsing: `parse_code_blocks()`

The parser reads the Markdown file line by line using `LinesIterator`, a
thin wrapper around a list of `(lineno, line)` pairs that supports both
forward iteration and bounded reverse iteration.

For each line that starts with ` ```python `, the parser:

1. Looks backward (and, for hidden blocks, forward) for an HTML comment
   containing metadata — see below.
2. If no metadata is found, skips the block.
3. If metadata is found, reads lines until the closing ` ``` ` fence.
4. Yields a `CodeBlock` dataclass with the source lines, start line
   number, name, and parsed arguments.

### Parsing HTML comments: `parse_arguments()`

This function handles two cases:

**Case 1 — Comment before the block (standard form):**

```
<!-- name: test_foo -->        ← comment ends with -->
```python                      ← parser is here
...
```
```

The reverse iterator looks back one non-blank line and finds `-->`. It
then scans further back to find the opening `<!--` and extracts the
key-value pairs.

**Case 2 — Block inside the comment (hidden form):**

```
<!--
name: test_foo
```python                      ← parser is here, inside a comment
...
```
-->
```

The reverse iterator does not find `-->` before the fence. The parser
then scans forward to find either `<!--` (meaning the block is not inside
a comment — skip it) or `-->` (meaning the block is inside the comment —
extract metadata from the lines between `<!--` and the fence).

### Grouping blocks: `compile_tests()`

After all `CodeBlock` objects are collected from the file, they are
grouped by name. Blocks with the same name are sorted by line number and
form one test.

### Building source: `_build_source()`

For a group of blocks, the plugin creates a source string of length equal
to the last line of the last block. Each block's lines are placed at their
original line numbers. Gaps are filled with empty strings. This preserves
line numbers in tracebacks: if a block starts at line 42, an
`AssertionError` on its first line reports `file.md:42`.

## The execution phase

Each test is a `MarkdownTest` item — a subclass of `pytest.Item`. Its
`runtest()` method:

1. Resolves requested fixtures using pytest's standard fixture resolution.
2. Compiles the source with `compile()` (using `PyCF_ALLOW_TOP_LEVEL_AWAIT`
   for async tests).
3. Executes the compiled code with `exec()` in a namespace that includes
   the injected fixture values.

### Subtests

When `case:` blocks are present, each case block is wrapped in:

```{code-block} python
with __markdown_pytest_subtests_fixture.test(msg='case_name line=N'):
    # case block code
```

The `subtests` fixture (built into pytest 9+) is automatically added to
the fixture list.

### Subprocess mode

For `subprocess: true` tests, `runtest()`:

1. Writes the combined source to a temporary file.
2. For async code, wraps the source in `async def __amain(): ...; asyncio.run(__amain())`.
3. Calls `subprocess.run([sys.executable, tmpfile])`.
4. Fails the test if the return code is non-zero, showing stderr as the
   failure message.

### REPL / doctest mode

For `repl: true` tests, the source is parsed by Python's `doctest` module
into a `DocTestRunner`. The runner executes each `>>>` example and compares
output. Failures are reported with the standard doctest diff format.

## Why HTML comments?

Alternative approaches considered:

- **YAML front matter** — would require all Markdown files to have front
  matter blocks. Not idiomatic for documentation files.
- **Special fence info strings** — ` ```python name=test_foo ` — not
  supported by most Markdown renderers; breaks syntax highlighting.
- **Separate `.yaml` sidecar files** — cumbersome; breaks the connection
  between test and example.

HTML comments are the only invisible, parseable construct available in
standard Markdown. They are ignored by all renderers and can contain
arbitrary text. The downside is that they require a line-by-line parser
rather than a standard Markdown AST parser — but this keeps the dependency
list short and makes parsing fast.

## Why line-by-line parsing?

A full Markdown AST parser (like `mistune` or `markdown-it-py`) would need
to expose comment nodes with their positions, which most parsers do not do.
It would also be an additional dependency. The hand-written line iterator
is 150 lines and handles the only cases that matter for test collection.

## Source line number preservation

Tracebacks pointing to the original Markdown file is a deliberate design
goal. The implementation pads the compiled source with blank lines so that
the Python line numbers match Markdown line numbers. This means a failing
test always shows the exact line to jump to, even in a file with thousands
of lines of prose.

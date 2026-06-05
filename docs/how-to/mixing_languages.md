# How to mix Python and non-Python code blocks

Markdown files that serve as documentation often contain code examples in
many languages — shell commands, JSON config, YAML, SQL, and more. markdown-
pytest collects only Python blocks that have a `name:` comment; everything
else is ignored.

## What is ignored

The following block types are **always** skipped:

- Blocks tagged with any language other than `python` (`` ```bash ``,
  `` ```json ``, `` ```yaml ``, `` ```sql ``, etc.)
- Blocks with no language tag (bare ` ``` `)
- Python blocks without a `<!-- name: ... -->` comment above them
- Blocks inside HTML comments that do not contain test metadata

## Shell command examples

Shell blocks pass through untouched:

````{code-block} markdown
```bash
pip install mypackage
```

```bash
$ mypackage --version
1.2.3
```
````

Both are invisible to pytest and cause no issues.

## JSON / YAML / TOML configuration examples

````{code-block} markdown
```json
{
  "host": "localhost",
  "port": 5432
}
```

```yaml
services:
  db:
    image: postgres:16
```

```toml
[tool.mypackage]
debug = true
```
````

All ignored. Only ` ```python ` blocks are considered.

## Bare code blocks

Blocks with no language tag are also ignored:

````{code-block} markdown
```
This is a plain text block.
It is not Python.
```
````

## Python blocks without a name comment

A Python block without the `<!-- name: ... -->` comment is not collected:

````{code-block} markdown
```python
# This block has no name comment — it is ignored by markdown-pytest
x = 1 + 1
```
````

This is by design — you can have documentation examples that are not tests.

## The `--md-prefix` option and ignoring blocks

By default, only names starting with `test` are collected. A Python block
with `<!-- name: example_foo -->` (no `test` prefix) is silently ignored.
This lets you use the comment syntax for other purposes without accidentally
creating tests.

## Mixed-language file example

A full README might look like:

````{code-block} text
## Installation

```bash
pip install mypackage
```

## Configuration

```yaml
mypackage:
  debug: false
```

## Usage

<!-- name: test_basic_usage -->
```python
import mypackage
result = mypackage.process([1, 2, 3])
assert result == [2, 4, 6]
```

Here is what the output looks like:

```
[2, 4, 6]
```

## API

```python
# This block shows the function signature — not a test
def process(items: list[int]) -> list[int]:
    ...
```
````

From this file, pytest collects exactly one test: `test_basic_usage`. All
other blocks are ignored.

## Indented blocks inside HTML elements

Code blocks inside `<details>` or similar HTML elements may be indented.
The plugin strips the leading indentation automatically:

````{code-block} markdown
<details>
<summary>Show example</summary>

    <!-- name: test_inside_details -->
    ```python
    assert 1 + 1 == 2
    ```

</details>
````

The four-space indentation caused by the `<details>` wrapper is removed
during parsing.

## Four-backtick fences

Fences using four backticks (```` ```` ````) instead of three are also
ignored, even if tagged as `python`. This is useful for showing Markdown
source that contains triple-backtick fences:

`````{code-block} markdown
````python
# This looks like Python but uses four backticks — ignored by markdown-pytest
x = 1
````
`````

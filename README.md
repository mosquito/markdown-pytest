markdown-pytest
===============

[![Github Actions](https://github.com/mosquito/markdown-pytest/workflows/tests/badge.svg)](https://github.com/mosquito/markdown-pytest/actions?query=workflow%3Atests)
[![PyPI Version](https://img.shields.io/pypi/v/markdown-pytest.svg)](https://pypi.python.org/pypi/markdown-pytest/)
[![PyPI Wheel](https://img.shields.io/pypi/wheel/markdown-pytest.svg)](https://pypi.python.org/pypi/markdown-pytest/)
[![Python Versions](https://img.shields.io/pypi/pyversions/markdown-pytest.svg)](https://pypi.python.org/pypi/markdown-pytest/)
[![License](https://img.shields.io/pypi/l/markdown-pytest.svg)](https://pypi.python.org/pypi/markdown-pytest/)

A `pytest` plugin that collects and executes Python code blocks from Markdown
files, so your documentation examples are always tested.

> **By the way:** this README is itself tested by `markdown-pytest`.
> Every Python code block below is a real test that runs on every CI build.

Quick start
-----------

Install with pip:

    pip install markdown-pytest

Place an HTML comment with a `name` key directly above a `python` code
fence. The plugin collects it as a test:

<!-- name: test_quick_start -->
```python
assert 2 + 2 == 4
```

Run it:

    $ pytest -v README.md

Sample output:

    README.md::test_quick_start PASSED
    README.md::test_example PASSED
    README.md::test_hidden_demo PASSED

That is the only requirement. Everything below is optional and lets you
handle progressively more complex scenarios.

Comment syntax
--------------

The comment format uses colon-separated key-value pairs, separated by
semicolons. The trailing semicolon is optional:

    <!-- key1: value1; key2: value2 -->

Comments can span multiple lines:

    <!--
        name: test_name;
        fixtures: tmp_path, monkeypatch
    -->

Both two-dash and three-dash variants are supported. All of the following
are parsed identically:

    <!--  name: test_name -->
    <!--- name: test_name --->
    <!--  name: test_name --->
    <!--- name: test_name -->

Available comment parameters:

* `name` (required) — the test name. Must start with `test` by default
  (see [Configuration](#configuration) to change the prefix).
* `case` — marks the block as a subtest (see [Subtests](#subtests)).
* `fixtures` — comma-separated list of pytest fixtures to inject
  (see [Fixtures](#fixtures)).

Fixture lists can be written in several ways:

    <!-- name: test_foo; fixtures: tmp_path, monkeypatch, capsys -->

    <!--
        name: test_foo;
        fixtures: tmp_path,
                  monkeypatch,
                  capsys
    -->

    <!--
        name: test_foo;
        fixtures: tmp_path;
        fixtures: monkeypatch;
        fixtures: capsys
    -->

Code blocks without a `name` comment are silently ignored — regular
documentation examples keep working as before.

Code split
----------

You can split a test across several code blocks by giving them the same
`name`. The blocks are combined into a single test, preserving source line
numbers for accurate tracebacks.

This block performs import:

<!-- name: test_example -->
```python
from itertools import chain
```

`chain` usage example:

<!-- name: test_example -->
```python
assert list(chain(range(2), range(2))) == [0, 1, 0, 1]
```

The split blocks do not need to be consecutive. Blocks with the same name
are combined even when separated by other tests:

<!-- name: test_non_consecutive_a -->
```python
value = 42
```

<!-- name: test_non_consecutive_helper -->
```python
assert True
```

<!-- name: test_non_consecutive_a -->
```python
assert value == 42
```

Subtests
--------

Add `case: case_name` to run a block as a subtest. Shared setup code goes
in a block without a `case`, and each subsequent `case` block runs as an
independent subtest:

<!-- name: test_counter -->
```python
from collections import Counter
```

<!--
    name: test_counter;
    case: initialize_counter
-->
```python
counter = Counter()
```

<!--
    name: test_counter;
    case: assign_counter_value
-->
```python
counter["foo"] += 1

assert counter["foo"] == 1
```

The [pytest-subtests](https://pypi.org/project/pytest-subtests/) package
is installed automatically as a dependency.

Fixtures
--------

You can request pytest fixtures by adding `fixtures: name1, name2` to the
comment. Any standard pytest fixture (`tmp_path`, `monkeypatch`, `capsys`,
`request`, etc.) or custom fixtures defined in `conftest.py` can be used.
The requested fixtures are available as variables in the code block.

### Single fixture

<!-- name: test_with_tmp_path; fixtures: tmp_path -->
```python
p = tmp_path / "hello.txt"
p.write_text("hello")
assert p.read_text() == "hello"
```

### Multiple fixtures

<!-- name: test_multi_fixtures; fixtures: tmp_path, monkeypatch -->
```python
import os
monkeypatch.setenv("DATA_DIR", str(tmp_path))
assert os.environ["DATA_DIR"] == str(tmp_path)
```

### Multiline fixture lists

Fixtures can span multiple lines using comma continuation:

<!--
    name: test_multiline_fixtures;
    fixtures: tmp_path,
              monkeypatch
-->
```python
import os
monkeypatch.setenv("ML_DIR", str(tmp_path))
assert os.environ["ML_DIR"] == str(tmp_path)
```

Or as separate semicolon-delimited entries — values for duplicate keys are
merged automatically:

<!--
    name: test_separate_fixtures;
    fixtures: tmp_path;
    fixtures: capsys
-->
```python
p = tmp_path / "out.txt"
p.write_text("ok")
print(p.read_text())
captured = capsys.readouterr()
assert captured.out.strip() == "ok"
```

### Fixtures with split blocks

Only the first block needs the `fixtures:` declaration. All blocks with the
same name share the namespace:

<!-- name: test_split_fixtures; fixtures: tmp_path -->
```python
p = tmp_path / "data.txt"
p.write_text("hello")
```

<!-- name: test_split_fixtures -->
```python
assert p.read_text() == "hello"
```

You can also declare different fixtures in different blocks — they are
merged together:

<!-- name: test_merged_fixtures; fixtures: tmp_path -->
```python
p = tmp_path / "output.txt"
p.write_text("merged")
```

<!-- name: test_merged_fixtures; fixtures: capsys -->
```python
print(p.read_text())
captured = capsys.readouterr()
assert captured.out.strip() == "merged"
```

### Fixtures with subtests

Fixtures and subtests (`case:`) can be freely combined:

<!-- name: test_fixture_cases; fixtures: tmp_path -->
```python
data_file = tmp_path / "data.txt"
```

<!-- name: test_fixture_cases; case: write -->
```python
data_file.write_text("hello world")
assert data_file.exists()
```

<!-- name: test_fixture_cases; case: read back -->
```python
assert data_file.read_text() == "hello world"
```

Hidden code blocks
------------------

A code block placed *inside* the comment is invisible to readers but runs
before the visible block. This is useful for imports, boilerplate, or test
data preparation:

<!--
name: test_hidden_init
```python
init_value = 123
```
-->
```python
assert init_value == 123
```

Readers see only `assert init_value == 123` — the assignment is hidden in
the HTML comment.

### Hidden setup, visible demo, hidden assertions

You can combine hidden blocks and split blocks to create documentation that
reads like a tutorial: the setup and assertions are invisible, and the reader
sees only the interesting part. This is the **recommended pattern** for
polished documentation examples.

The following example demonstrates a CSV parser. The reader sees only the
parsing logic — file creation and assertions are hidden:

<!--
name: test_hidden_demo;
fixtures: tmp_path
```python
csv_file = tmp_path / "users.csv"
csv_file.write_text("name,role\nAlice,admin\nBob,viewer\n")
```
-->
```python
rows = []
for line in csv_file.read_text().strip().split("\n")[1:]:
    name, role = line.split(",")
    rows.append({"name": name, "role": role})
```

<!--
name: test_hidden_demo
```python
assert len(rows) == 2
assert rows[0] == {"name": "Alice", "role": "admin"}
assert rows[1] == {"name": "Bob", "role": "viewer"}
```
-->

Readers see only the `for` loop that parses CSV rows. The file creation
(using `tmp_path`) and the assertions are both hidden inside HTML comments.
Fixtures are available inside hidden blocks, so you can perform invisible
setup using any requested fixture.

Mixing with other languages
---------------------------

Markdown files often contain non-Python code blocks. The plugin safely
skips any fenced block that is not tagged as `python` — including
` ```bash `, ` ```json `, ` ```yaml `, bare ` ``` ` blocks, and
four-backtick (```` ```` ````) fences:

    ```bash
    echo "this is ignored by markdown-pytest"
    ```

    ```json
    {"this": "is also ignored"}
    ```

    ```
    Bare fences without a language tag are ignored too.
    ```

Only blocks explicitly tagged ` ```python ` and preceded by a
`<!-- name: ... -->` comment are collected as tests.

Indented code blocks
--------------------

Code blocks inside HTML elements like `<details>` may be indented.
The plugin strips the leading indentation automatically:

<details>
<summary>Indented example</summary>

    <!-- name: test_indented -->
    ```python
    assert True
    ```

</details>

Configuration
-------------

### Test prefix

By default only blocks whose `name` starts with `test` are collected.
Use `--md-prefix` to change the prefix:

    $ pytest --md-prefix=check README.md

The prefix can also be set permanently in `pyproject.toml`:

    [tool.pytest.ini_options]
    addopts = "--md-prefix=check"

Or in `pytest.ini` / `setup.cfg`:

    [pytest]
    addopts = --md-prefix=check

Supported environments
----------------------

* **Python** >= 3.10 (CPython and PyPy)
* Both `.md` and `.markdown` file extensions are collected automatically
* The plugin auto-registers via the `pytest11` entry point — no
  configuration is needed beyond `pip install`
* Tracebacks from failing tests preserve the original Markdown line numbers,
  so you can jump straight to the source

Why test Markdown code blocks?
------------------------------

Documentation with code examples tends to rot. APIs change, function
signatures evolve, and the snippets in your README silently become wrong.
Readers copy-paste broken examples, file issues, and lose trust in the
project.

The usual workaround is to maintain a parallel test suite that duplicates the
same logic. Now you have two copies that can drift apart. `markdown-pytest`
removes that duplication: the documentation **is** the test.

By running `pytest` against your `.md` files you get:

* **Guaranteed accuracy** — every code sample in your docs is executed on
  every CI run.
* **Zero duplication** — there is only one copy of the example code, living
  in the prose where readers expect it.
* **Natural documentation** — Markdown is rendered on GitHub, PyPI, and
  documentation sites. Your tests look like ordinary code examples to
  readers.

Why HTML comments?
------------------

Markdown has no built-in way to attach metadata to a code block. The
`markdown-pytest` plugin uses HTML comments because they are:

* **Invisible to readers** — rendered Markdown hides HTML comments, so the
  test markers never clutter the documentation.
* **Part of the Markdown spec** — every parser preserves them, unlike
  non-standard directive syntaxes.
* **Easy to type** — `<!-- name: test_foo -->` is short and obvious.
* **Extensible** — semicolon-separated key-value pairs allow adding
  parameters (like `case` or `fixtures`) without inventing a new format.

The comment must be placed directly above the code fence it annotates.
The `name` key is required; blocks without it are silently ignored so that
regular documentation examples keep working as before.

Best practices
--------------

**Keep examples self-contained.** Each test should make sense on its own.
A reader scanning the documentation should not have to scroll back through
several sections to understand what a code block does.

**Use split blocks for narrative flow.** When an example naturally spans
several steps (import, setup, usage), split it into multiple blocks with the
same `name` and add explanatory prose between them.

**Use hidden blocks for boilerplate.** If a test needs imports or setup that
would distract the reader, put them in a hidden code block inside the
comment. The rendered documentation stays clean while the test remains
complete.

**Use fixtures instead of mocking by hand.** Requesting `tmp_path`,
`monkeypatch`, or `capsys` via the `fixtures:` parameter keeps tests short
and idiomatic. Custom `conftest.py` fixtures work too — use them to share
setup across multiple Markdown files.

**Prefer subtests for variations.** When you have several related assertions,
use `case:` blocks. Pytest reports each subtest independently, so a failure
in one does not hide the others.

**Run the docs in CI.** Add your `.md` files to the pytest invocation in
your CI pipeline. Stale examples will break the build before they reach
users.

**Split tests into focused files.** Rather than putting all tests in a single
huge Markdown file, organize them by topic — for example
`tests/fixtures.md`, `tests/splitting.md`, and so on. This makes failures
easier to locate and keeps each file readable.

**Name tests descriptively.** The test name appears in pytest output. A name
like `test_csv_parsing` is more helpful than `test_example_1` when something
fails.

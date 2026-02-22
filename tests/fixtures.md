Fixtures support
----------------

<!-- name: test_fixtures_tmp_path; fixtures: tmp_path -->
```python
p = tmp_path / "hello.txt"
p.write_text("hello")
assert p.read_text() == "hello"
```

<!-- name: test_fixtures_capsys; fixtures: capsys -->
```python
print("hello")
captured = capsys.readouterr()
assert captured.out == "hello\n"
```

<!-- name: test_fixtures_monkeypatch; fixtures: monkeypatch -->
```python
import os
monkeypatch.setenv("MARKDOWN_PYTEST_TEST", "1")
assert os.environ["MARKDOWN_PYTEST_TEST"] == "1"
```

<!-- name: test_fixtures_multiple; fixtures: tmp_path, monkeypatch -->
```python
import os
monkeypatch.setenv("MARKDOWN_PYTEST_DIR", str(tmp_path))
assert os.environ["MARKDOWN_PYTEST_DIR"] == str(tmp_path)
```

Fixtures with split blocks
--------------------------

Only the first block needs the `fixtures:` declaration, all blocks
share the same namespace.

<!-- name: test_fixtures_split; fixtures: tmp_path -->
```python
p = tmp_path / "split.txt"
p.write_text("part1")
```

<!-- name: test_fixtures_split -->
```python
assert p.read_text() == "part1"
p.write_text("part2")
assert p.read_text() == "part2"
```

Multiple fixtures across split blocks — the first block declares both,
subsequent blocks use them freely.

<!-- name: test_fixtures_split_multiple; fixtures: tmp_path, monkeypatch -->
```python
import os
monkeypatch.setenv("MARKDOWN_SPLIT_DIR", str(tmp_path))
```

<!-- name: test_fixtures_split_multiple -->
```python
assert os.environ["MARKDOWN_SPLIT_DIR"] == str(tmp_path)
p = tmp_path / "env.txt"
p.write_text(os.environ["MARKDOWN_SPLIT_DIR"])
```

<!-- name: test_fixtures_split_multiple -->
```python
assert p.read_text() == str(tmp_path)
```

Fixtures declared across different split blocks — both blocks declare
fixtures, they are merged together.

<!-- name: test_fixtures_split_merged; fixtures: tmp_path -->
```python
p = tmp_path / "output.txt"
```

<!-- name: test_fixtures_split_merged; fixtures: capsys -->
```python
print(str(p))
captured = capsys.readouterr()
assert captured.out.strip() == str(p)
```

Split blocks with fixtures and subtests combined.

<!-- name: test_fixtures_split_subtests; fixtures: tmp_path -->
```python
data_file = tmp_path / "data.txt"
```

<!-- name: test_fixtures_split_subtests; case: write -->
```python
data_file.write_text("hello world")
assert data_file.exists()
```

<!-- name: test_fixtures_split_subtests; case: read back -->
```python
assert data_file.read_text() == "hello world"
```

Multiline comment with fixtures
-------------------------------

<!--
    name: test_fixtures_multiline_comment;
    fixtures: tmp_path
-->
```python
p = tmp_path / "multiline.txt"
p.write_text("from multiline comment")
assert p.read_text() == "from multiline comment"
```

<!---
    name: test_fixtures_multiline_multiple;
    fixtures: tmp_path, monkeypatch, capsys
--->
```python
import os
monkeypatch.setenv("MULTILINE_TEST", str(tmp_path))
print(os.environ["MULTILINE_TEST"])
captured = capsys.readouterr()
assert captured.out.strip() == str(tmp_path)
```

<!--
    name: test_fixtures_multiline_split;
    fixtures: tmp_path, monkeypatch
-->
```python
import os
monkeypatch.setenv("SPLIT_ML", "yes")
```

<!--
    name: test_fixtures_multiline_split
-->
```python
assert os.environ["SPLIT_ML"] == "yes"
p = tmp_path / "ml.txt"
p.write_text("multiline split")
assert p.read_text() == "multiline split"
```

Many fixtures at once
---------------------

<!-- name: test_fixtures_many; fixtures: tmp_path, monkeypatch, capsys, request, cache, record_property, record_testsuite_property, tmp_path_factory, recwarn, doctest_namespace -->
```python
import os
import warnings

# tmp_path: write a file
p = tmp_path / "many.txt"
p.write_text("many fixtures")
assert p.read_text() == "many fixtures"

# monkeypatch: set env
monkeypatch.setenv("MANY_FIXTURES", "1")
assert os.environ["MANY_FIXTURES"] == "1"

# capsys: capture output
print("captured")
captured = capsys.readouterr()
assert captured.out == "captured\n"

# request: access test metadata
assert request.node.name == "test_fixtures_many"

# cache: store and retrieve values
cache.set("fixtures/test_key", 42)
assert cache.get("fixtures/test_key", None) == 42

# record_property: attach metadata to test
record_property("fixture_count", 10)

# record_testsuite_property: attach suite-level metadata
record_testsuite_property("suite_name", "fixtures")

# tmp_path_factory: create additional temp dirs
extra = tmp_path_factory.mktemp("extra")
assert extra.is_dir()

# recwarn: capture warnings
warnings.warn("test warning", UserWarning)
w = recwarn.pop(UserWarning)
assert "test warning" in str(w.message)

# doctest_namespace: verify it's a dict
assert isinstance(doctest_namespace, dict)
```

Duplicate fixture names
-----------------------

Requesting the same fixture twice should not cause errors.

<!-- name: test_fixtures_duplicate; fixtures: tmp_path, tmp_path -->
```python
p = tmp_path / "dedup.txt"
p.write_text("no duplicates")
assert p.read_text() == "no duplicates"
```

Explicit subtests in fixtures
-----------------------------

User accidentally lists `subtests` in fixtures — should still work.

<!-- name: test_fixtures_explicit_subtests; fixtures: tmp_path, subtests -->
```python
p = tmp_path / "subtests.txt"
p.write_text("explicit")
assert p.read_text() == "explicit"
```

Hidden code block with fixtures
-------------------------------

Fixtures combined with the hidden code block inside a comment.

<!--
name: test_fixtures_hidden_block;
fixtures: tmp_path
```python
secret_value = 42
```
-->
```python
p = tmp_path / "hidden.txt"
p.write_text(str(secret_value))
assert p.read_text() == "42"
```

Four backticks with fixtures
----------------------------

<!--- name: test_fixtures_four_backticks; fixtures: tmp_path -->
````python
p = tmp_path / "backticks.txt"
p.write_text("four backticks")
assert p.read_text() == "four backticks"
````

Subtests with multiple fixtures
-------------------------------

<!-- name: test_fixtures_subtests_multi; fixtures: tmp_path, monkeypatch -->
```python
import os
base = tmp_path / "subtests_multi"
base.mkdir()
```

<!-- name: test_fixtures_subtests_multi; case: setup env -->
```python
monkeypatch.setenv("SUBTEST_DIR", str(base))
assert os.environ["SUBTEST_DIR"] == str(base)
```

<!-- name: test_fixtures_subtests_multi; case: write file -->
```python
p = base / "test.txt"
p.write_text(os.environ["SUBTEST_DIR"])
assert p.exists()
```

<!-- name: test_fixtures_subtests_multi; case: verify -->
```python
assert p.read_text() == str(base)
```

Non-consecutive split with fixtures
------------------------------------

Fixture blocks separated by a different test.

<!-- name: test_fixtures_non_consecutive; fixtures: tmp_path -->
```python
nc_file = tmp_path / "nc.txt"
nc_file.write_text("part1")
```

<!-- name: test_fixtures_nc_separator -->
```python
assert True
```

<!-- name: test_fixtures_non_consecutive -->
```python
assert nc_file.read_text() == "part1"
nc_file.write_text("part2")
assert nc_file.read_text() == "part2"
```

Multiline fixtures list
-----------------------

Comma-continuation across lines:

<!--
    name: test_fixtures_multiline_list;
    fixtures: tmp_path,
              monkeypatch,
              capsys
-->
```python
import os
monkeypatch.setenv("ML_LIST", str(tmp_path))
print(os.environ["ML_LIST"])
captured = capsys.readouterr()
assert captured.out.strip() == str(tmp_path)
```

Separate semicolon-delimited fixture entries:

<!--
    name: test_fixtures_separate_lines;
    fixtures: tmp_path;
    fixtures: monkeypatch;
    fixtures: capsys
-->
```python
import os
monkeypatch.setenv("SEP_LINES", str(tmp_path))
print(os.environ["SEP_LINES"])
captured = capsys.readouterr()
assert captured.out.strip() == str(tmp_path)
```

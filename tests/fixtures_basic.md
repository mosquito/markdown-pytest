Basic fixtures
==============

Single fixture: tmp_path

<!-- name: test_fixtures_tmp_path; fixtures: tmp_path -->
```python
p = tmp_path / "hello.txt"
p.write_text("hello")
assert p.read_text() == "hello"
```

Single fixture: capsys

<!-- name: test_fixtures_capsys; fixtures: capsys -->
```python
print("hello")
captured = capsys.readouterr()
assert captured.out == "hello\n"
```

Single fixture: monkeypatch

<!-- name: test_fixtures_monkeypatch; fixtures: monkeypatch -->
```python
import os
monkeypatch.setenv("MARKDOWN_PYTEST_TEST", "1")
assert os.environ["MARKDOWN_PYTEST_TEST"] == "1"
```

Multiple fixtures on one line

<!-- name: test_fixtures_multiple; fixtures: tmp_path, monkeypatch -->
```python
import os
monkeypatch.setenv("MARKDOWN_PYTEST_DIR", str(tmp_path))
assert os.environ["MARKDOWN_PYTEST_DIR"] == str(tmp_path)
```

Multiline comment with single fixture

<!--
    name: test_fixtures_multiline_comment;
    fixtures: tmp_path
-->
```python
p = tmp_path / "multiline.txt"
p.write_text("from multiline comment")
assert p.read_text() == "from multiline comment"
```

Multiline comment with multiple fixtures (three dashes)

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

Multiline fixture list with comma continuation

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

Separate semicolon-delimited fixture entries

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

Edge cases
----------

Requesting the same fixture twice should not cause errors.

<!-- name: test_fixtures_duplicate; fixtures: tmp_path, tmp_path -->
```python
p = tmp_path / "dedup.txt"
p.write_text("no duplicates")
assert p.read_text() == "no duplicates"
```

User accidentally lists `subtests` in fixtures — should still work.

<!-- name: test_fixtures_explicit_subtests; fixtures: tmp_path, subtests -->
```python
p = tmp_path / "subtests.txt"
p.write_text("explicit")
assert p.read_text() == "explicit"
```

Four backticks with fixtures

<!--- name: test_fixtures_four_backticks; fixtures: tmp_path -->
````python
p = tmp_path / "backticks.txt"
p.write_text("four backticks")
assert p.read_text() == "four backticks"
````

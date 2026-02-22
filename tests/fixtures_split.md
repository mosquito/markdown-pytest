Fixtures with split blocks
==========================

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

Split blocks with multiline fixtures in the comment.

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

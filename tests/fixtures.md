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

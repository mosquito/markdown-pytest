Interleaved tests with hidden init and fixtures
================================================

Two independent tests interleaved — each has its own hidden init,
fixtures, and visible blocks, separated by each other.

<!--
name: test_interleaved_alpha;
fixtures: tmp_path
```python
alpha_data = {"key": "alpha_value"}
```
-->
```python
alpha_file = tmp_path / "alpha.txt"
alpha_file.write_text(alpha_data["key"])
```

<!--
name: test_interleaved_beta;
fixtures: tmp_path, monkeypatch
```python
import os
beta_prefix = "BETA"
```
-->
```python
monkeypatch.setenv(f"{beta_prefix}_ACTIVE", "1")
beta_file = tmp_path / "beta.txt"
beta_file.write_text(os.environ[f"{beta_prefix}_ACTIVE"])
```

<!-- name: test_interleaved_alpha -->
```python
assert alpha_file.read_text() == "alpha_value"
alpha_file.write_text("updated")
assert alpha_file.read_text() == "updated"
```

<!-- name: test_interleaved_beta -->
```python
assert beta_file.read_text() == "1"
assert os.environ[f"{beta_prefix}_ACTIVE"] == "1"
```

Three-way interleave with hidden init, fixtures, and subtests:

<!--
name: test_interleaved_writer;
fixtures: tmp_path
```python
files_written = []
```
-->
```python
for name in ["a", "b", "c"]:
    p = tmp_path / f"{name}.txt"
    p.write_text(f"content_{name}")
    files_written.append(p)
```

<!-- name: test_interleaved_simple_check -->
```python
assert 1 + 1 == 2
```

<!--
name: test_interleaved_reader;
fixtures: tmp_path
```python
expected = {"x": 10, "y": 20}
```
-->
```python
for key, value in expected.items():
    p = tmp_path / f"{key}.dat"
    p.write_text(str(value))
```

<!-- name: test_interleaved_writer -->
```python
assert len(files_written) == 3
for p in files_written:
    assert p.exists()
    assert p.read_text().startswith("content_")
```

<!-- name: test_interleaved_reader; case: verify files -->
```python
for key, value in expected.items():
    p = tmp_path / f"{key}.dat"
    assert p.read_text() == str(value)
```

<!-- name: test_interleaved_reader; case: count files -->
```python
dat_files = list(tmp_path.glob("*.dat"))
assert len(dat_files) == len(expected)
```

Interleaved hidden init with capsys:

<!--
name: test_interleaved_output;
fixtures: capsys
```python
messages = ["hello", "world", "!"]
```
-->
```python
for msg in messages:
    print(msg)
```

<!-- name: test_interleaved_counter -->
```python
assert sum(range(10)) == 45
```

<!-- name: test_interleaved_output -->
```python
captured = capsys.readouterr()
lines = captured.out.strip().split("\n")
assert lines == messages
```

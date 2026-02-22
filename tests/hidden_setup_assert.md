Hidden setup and assertions
===========================

The "hidden setup, visible demo, hidden assert" pattern lets
documentation show only the interesting part of an example. The
boilerplate (file creation, environment prep, assertions) lives in
hidden blocks invisible to the reader.

### JSON round-trip

<!--
name: test_hidden_json_roundtrip;
fixtures: tmp_path
```python
import json
config = {"host": "localhost", "port": 8080, "debug": True}
config_file = tmp_path / "config.json"
config_file.write_text(json.dumps(config, indent=2))
```
-->
```python
import json
with open(config_file) as f:
    loaded = json.load(f)
```

<!--
name: test_hidden_json_roundtrip
```python
assert loaded == config
assert loaded["port"] == 8080
assert loaded["debug"] is True
```
-->

### Text processing pipeline

<!--
name: test_hidden_text_pipeline;
fixtures: tmp_path
```python
raw = tmp_path / "raw.txt"
raw.write_text("  Hello World  \n  foo BAR  \n  Baz Qux  \n")
```
-->
```python
lines = raw.read_text().strip().split("\n")
cleaned = [line.strip().lower() for line in lines]
```

<!--
name: test_hidden_text_pipeline
```python
assert cleaned == ["hello world", "foo bar", "baz qux"]
```
-->

### Environment-based configuration

<!--
name: test_hidden_env_config;
fixtures: monkeypatch
```python
import os
monkeypatch.setenv("APP_HOST", "0.0.0.0")
monkeypatch.setenv("APP_PORT", "9000")
monkeypatch.setenv("APP_DEBUG", "true")
```
-->
```python
import os
host = os.environ.get("APP_HOST", "127.0.0.1")
port = int(os.environ.get("APP_PORT", "8000"))
debug = os.environ.get("APP_DEBUG", "false").lower() == "true"
```

<!--
name: test_hidden_env_config
```python
assert host == "0.0.0.0"
assert port == 9000
assert debug is True
```
-->

### Directory tree builder

<!--
name: test_hidden_tree_builder;
fixtures: tmp_path
```python
for name in ["src", "tests", "docs"]:
    (tmp_path / name).mkdir()
(tmp_path / "src" / "__init__.py").write_text("")
(tmp_path / "src" / "main.py").write_text("print('hello')\n")
(tmp_path / "tests" / "test_main.py").write_text("assert True\n")
```
-->
```python
src_files = sorted(p.name for p in (tmp_path / "src").iterdir())
dirs = sorted(p.name for p in tmp_path.iterdir() if p.is_dir())
```

<!--
name: test_hidden_tree_builder
```python
assert dirs == ["docs", "src", "tests"]
assert src_files == ["__init__.py", "main.py"]
assert (tmp_path / "tests" / "test_main.py").read_text() == "assert True\n"
```
-->

### Captured output verification

<!--
name: test_hidden_output_capture;
fixtures: capsys
```python
expected_lines = ["Starting...", "Processing 3 items", "Done."]
```
-->
```python
print("Starting...")
for i in range(3):
    pass
print(f"Processing 3 items")
print("Done.")
```

<!--
name: test_hidden_output_capture
```python
captured = capsys.readouterr()
lines = captured.out.strip().split("\n")
assert lines == expected_lines
```
-->

### Multi-step data transformation

<!--
name: test_hidden_data_transform;
fixtures: tmp_path
```python
data_file = tmp_path / "scores.txt"
data_file.write_text("alice:90\nbob:85\ncharlie:92\n")
```
-->

Read raw scores:

```python
raw = data_file.read_text().strip().split("\n")
scores = {}
for entry in raw:
    name, score = entry.split(":")
    scores[name] = int(score)
```

Compute the average:

<!-- name: test_hidden_data_transform -->
```python
average = sum(scores.values()) / len(scores)
```

<!--
name: test_hidden_data_transform
```python
assert scores == {"alice": 90, "bob": 85, "charlie": 92}
assert average == (90 + 85 + 92) / 3
```
-->

### CSV parser demo

<!--
name: test_hidden_demo_csv;
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
name: test_hidden_demo_csv
```python
assert len(rows) == 2
assert rows[0] == {"name": "Alice", "role": "admin"}
assert rows[1] == {"name": "Bob", "role": "viewer"}
```
-->

### Environment-based config demo

<!--
name: test_hidden_demo_env;
fixtures: monkeypatch
```python
import os
monkeypatch.setenv("DB_HOST", "db.example.com")
monkeypatch.setenv("DB_PORT", "5432")
```
-->
```python
import os
db_host = os.environ["DB_HOST"]
db_port = int(os.environ["DB_PORT"])
connection_string = f"{db_host}:{db_port}"
```

<!--
name: test_hidden_demo_env
```python
assert connection_string == "db.example.com:5432"
```
-->

### Directory scanner demo

<!--
name: test_hidden_demo_scan;
fixtures: tmp_path
```python
(tmp_path / "src").mkdir()
(tmp_path / "src" / "app.py").write_text("# app")
(tmp_path / "src" / "utils.py").write_text("# utils")
(tmp_path / "README.md").write_text("# project")
```
-->
```python
py_files = sorted(
    p.name for p in tmp_path.rglob("*.py")
)
```

<!--
name: test_hidden_demo_scan
```python
assert py_files == ["app.py", "utils.py"]
```
-->

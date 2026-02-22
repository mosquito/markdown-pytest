Hidden code blocks with fixtures
=================================

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

Fixtures used directly inside the hidden block — `tmp_path` creates a
file tree that the visible block then verifies:

<!--
name: test_fixtures_in_hidden;
fixtures: tmp_path
```python
data_dir = tmp_path / "data"
data_dir.mkdir()
(data_dir / "a.txt").write_text("aaa")
(data_dir / "b.txt").write_text("bbb")
```
-->
```python
files = sorted(p.name for p in data_dir.iterdir())
assert files == ["a.txt", "b.txt"]
assert (data_dir / "a.txt").read_text() == "aaa"
```

Multiple fixtures used inside the hidden block:

<!--
name: test_fixtures_in_hidden_multi;
fixtures: tmp_path, monkeypatch
```python
import os
monkeypatch.setenv("HIDDEN_DIR", str(tmp_path))
config_file = tmp_path / "config.ini"
config_file.write_text("setting=on")
```
-->
```python
assert os.environ["HIDDEN_DIR"] == str(tmp_path)
assert config_file.read_text() == "setting=on"
```

capsys used inside the hidden block to consume expected output:

<!--
name: test_fixtures_in_hidden_capsys;
fixtures: capsys
```python
print("setup noise")
capsys.readouterr()
```
-->
```python
print("real output")
captured = capsys.readouterr()
assert captured.out == "real output\n"
```

monkeypatch used inside the hidden block for transparent env setup:

<!--
name: test_fixtures_in_hidden_monkeypatch;
fixtures: monkeypatch
```python
import os
monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
monkeypatch.setenv("SECRET_KEY", "s3cret")
```
-->
```python
assert os.environ["DATABASE_URL"] == "sqlite:///test.db"
assert os.environ["SECRET_KEY"] == "s3cret"
```

Hidden block uses tmp_path_factory to prepare multiple temp dirs:

<!--
name: test_fixtures_in_hidden_factory;
fixtures: tmp_path_factory
```python
src_dir = tmp_path_factory.mktemp("src")
dst_dir = tmp_path_factory.mktemp("dst")
(src_dir / "file.txt").write_text("original")
```
-->
```python
import shutil
shutil.copy2(src_dir / "file.txt", dst_dir / "file.txt")
assert (dst_dir / "file.txt").read_text() == "original"
```

Hidden init with fixtures and multiline fixture list:

<!--
name: test_fixtures_in_hidden_multiline;
fixtures: tmp_path,
          capsys
```python
greeting = "hello from hidden init"
```
-->
```python
p = tmp_path / "greeting.txt"
p.write_text(greeting)
print(p.read_text())
captured = capsys.readouterr()
assert captured.out.strip() == greeting
```

Hidden init in a split block — hidden code runs before the visible blocks:

<!--
name: test_fixtures_hidden_split;
fixtures: tmp_path
```python
base_dir = tmp_path / "project"
base_dir.mkdir()
```
-->
```python
src = base_dir / "src"
src.mkdir()
```

<!-- name: test_fixtures_hidden_split -->
```python
init = src / "__init__.py"
init.write_text("# package")
assert init.read_text() == "# package"
assert base_dir.exists()
```

Hidden init with subtests and fixtures:

<!--
name: test_fixtures_hidden_subtests;
fixtures: tmp_path
```python
data = {"a": 1, "b": 2, "c": 3}
output_dir = tmp_path / "output"
output_dir.mkdir()
```
-->
```python
total = sum(data.values())
assert total == 6
```

<!-- name: test_fixtures_hidden_subtests; case: write entries -->
```python
for key, value in data.items():
    (output_dir / f"{key}.txt").write_text(str(value))
assert len(list(output_dir.iterdir())) == 3
```

<!-- name: test_fixtures_hidden_subtests; case: read entries -->
```python
for key, value in data.items():
    content = (output_dir / f"{key}.txt").read_text()
    assert content == str(value)
```

Hidden init with separate fixtures entries:

<!--
name: test_fixtures_hidden_separate;
fixtures: tmp_path;
fixtures: monkeypatch
```python
import os
default_name = "markdown-pytest"
```
-->
```python
monkeypatch.setenv("APP_NAME", default_name)
p = tmp_path / "app.txt"
p.write_text(os.environ["APP_NAME"])
assert p.read_text() == default_name
```

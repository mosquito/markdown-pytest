Non-Python fenced blocks between tests
=======================================

Tests interleaved with non-Python fenced code blocks. The parser must
correctly skip ``bash``, ``json``, ``yaml``, and bare fenced blocks
without consuming the Python test blocks that follow them.

A bash example before the first test:

```bash
pytest -v tests/non_python_fences.md
```

<!-- name: test_after_bash_block -->
```python
assert 1 + 1 == 2
```

A JSON example between two tests:

```json
{"key": "value", "number": 42}
```

<!-- name: test_after_json_block -->
```python
import json
data = json.loads('{"key": "value", "number": 42}')
assert data["key"] == "value"
assert data["number"] == 42
```

A YAML-like example followed by another test:

```yaml
name: markdown-pytest
version: 1.0
features:
  - fixtures
  - split blocks
```

<!-- name: test_after_yaml_block -->
```python
features = ["fixtures", "split blocks"]
assert len(features) == 2
assert "fixtures" in features
```

A bare fenced block (no language) between tests:

```
This is a plain code block with no language specified.
It should be skipped by the parser.
```

<!-- name: test_after_bare_fence -->
```python
assert "skipped" != "consumed"
```

Multiple non-Python blocks in a row before a test:

```bash
echo "first"
```

```json
[1, 2, 3]
```

```
plain text
```

<!-- name: test_after_multiple_fences -->
```python
assert True
```

Four-backtick non-Python block:

````bash
echo "four backticks"
````

<!-- name: test_after_four_backtick_fence -->
```python
assert 4 > 3
```

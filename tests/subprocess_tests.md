# Subprocess Tests

Tests using the `subprocess: true` directive to run code in a
separate Python process.

## Basic subprocess test

<!-- name: test_subprocess_basic; subprocess: true -->
```python
assert 1 + 1 == 2
```

## Subprocess with imports

Subprocess tests can freely import without affecting the parent process.

<!-- name: test_subprocess_import; subprocess: true -->
```python
import json
data = json.dumps({"key": "value"})
parsed = json.loads(data)
assert parsed["key"] == "value"
```

## Subprocess split blocks

Multiple blocks with the same name are combined before running in
a subprocess.

<!-- name: test_subprocess_split; subprocess: true -->
```python
from collections import deque
queue = deque(maxlen=3)
```

Append items across split blocks:

<!-- name: test_subprocess_split; subprocess: true -->
```python
queue.append("a")
queue.append("b")
assert list(queue) == ["a", "b"]
```

Verify final state:

<!-- name: test_subprocess_split; subprocess: true -->
```python
queue.append("c")
queue.append("d")
assert list(queue) == ["b", "c", "d"]
```

## Hidden block with subprocess

Hidden setup code combined with a visible subprocess test block.

<!--
name: test_subprocess_hidden;
subprocess: true
```python
_secret = 42
```
-->
```python
assert _secret == 42
```

## Hidden setup and hidden assert

Hidden blocks on both sides, visible block in between, all
running as a subprocess.

<!--
name: test_subprocess_hidden_setup_assert;
subprocess: true
```python
import os as _os
_items = list(range(5))
```
-->

```python
total = sum(_items)
```

<!--
name: test_subprocess_hidden_setup_assert;
subprocess: true
```python
assert total == 10
assert len(_items) == 5
```
-->

## Interleaved subprocess and regular tests

A subprocess test interleaved with a regular in-process test.

<!-- name: test_subprocess_interleaved_sub; subprocess: true -->
```python
x = 10
```

<!-- name: test_subprocess_interleaved_regular -->
```python
y = 20
assert y == 20
```

<!-- name: test_subprocess_interleaved_sub; subprocess: true -->
```python
x += 5
assert x == 15
```

<!-- name: test_subprocess_interleaved_regular -->
```python
y += 10
assert y == 30
```

## Non-Python fences between subprocess blocks

Subprocess split blocks separated by non-Python fenced blocks.

```bash
echo "this is a bash block"
```

<!-- name: test_subprocess_non_python_fence; subprocess: true -->
```python
result = []
```

```json
{"status": "between blocks"}
```

<!-- name: test_subprocess_non_python_fence; subprocess: true -->
```python
result.append(1)
result.append(2)
```

```yaml
status: still between blocks
```

<!-- name: test_subprocess_non_python_fence; subprocess: true -->
```python
assert result == [1, 2]
```

## Subprocess isolation

Modifying global state in a subprocess does not leak into the
parent process or other tests.

<!-- name: test_subprocess_isolation; subprocess: true -->
```python
import sys
sys.modules["__subprocess_marker__"] = True
assert "__subprocess_marker__" in sys.modules
```

Verify the marker is not present in the parent process:

<!-- name: test_subprocess_isolation_check -->
```python
import sys
assert "__subprocess_marker__" not in sys.modules
```

## Non-consecutive subprocess split

Two subprocess blocks for the same test separated by an entirely
different test.

<!-- name: test_subprocess_non_consecutive; subprocess: true -->
```python
counter = {"value": 0}
```

<!-- name: test_subprocess_separator -->
```python
assert "this test separates the subprocess blocks"
```

<!-- name: test_subprocess_non_consecutive; subprocess: true -->
```python
counter["value"] += 1
assert counter["value"] == 1
```

## Four-backtick fence in subprocess

<!-- name: test_subprocess_four_backticks; subprocess: true -->
````python
assert 2 ** 10 == 1024
````

# Mark Tests

Tests for the `mark:` comment parameter.

## Simple xfail

<!-- name: test_mark_xfail; mark: xfail -->
```python
assert False, "expected to fail"
```

## xfail with reason

<!-- name: test_mark_xfail_reason; mark: xfail(reason="not implemented yet") -->
```python
assert False, "not implemented"
```

## xfail with raises

<!-- name: test_mark_xfail_raises; mark: xfail(raises=ZeroDivisionError) -->
```python
1 / 0
```

## skip with reason

<!-- name: test_mark_skip; mark: skip(reason="requires network") -->
```python
import urllib.request
urllib.request.urlopen("http://localhost:99999")
```

## Mark on split blocks

<!-- name: test_mark_split; mark: xfail -->
```python
x = 1
```

<!-- name: test_mark_split -->
```python
assert x == 2, "expected to fail"
```

## Mark on hidden blocks

<!--
name: test_mark_hidden;
mark: xfail(raises=ZeroDivisionError)
```python
x = 1
```
-->
```python
x / 0
```

## Mark with fixtures

<!-- name: test_mark_fixtures; mark: xfail; fixtures: tmp_path -->
```python
p = tmp_path / "nonexistent" / "deep" / "path" / "file.txt"
assert p.read_text() == "impossible"
```

## Mark with subprocess

<!-- name: test_mark_subprocess; mark: xfail; subprocess: true -->
```python
assert False, "expected subprocess failure"
```

## Multiple marks via separate entries

<!--
    name: test_mark_multiple;
    mark: xfail;
    mark: strict
-->
```python
assert False, "expected to fail strictly"
```

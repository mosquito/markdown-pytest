import textwrap

import pytest

from markdown_pytest import (
    _build_source, compile_code_blocks, parse_code_blocks,
)


@pytest.fixture()
def md_file(tmp_path):
    def factory(content):
        p = tmp_path / "test.md"
        p.write_text(textwrap.dedent(content))
        return str(p)

    return factory


def parse_blocks(md_file, content):
    return list(parse_code_blocks(md_file(content)))


def test_consecutive_blocks_combined(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a -->
        ```python
        x = 1
        ```

        <!-- name: test_a -->
        ```python
        assert x == 1
        ```
    """,
    )
    assert len(blocks) == 2
    assert all(b.name == "test_a" for b in blocks)

    code = compile_code_blocks(*blocks)
    assert code is not None
    exec(code)


def test_non_consecutive_blocks_combined(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a -->
        ```python
        x = 1
        ```

        <!-- name: test_b -->
        ```python
        assert True
        ```

        <!-- name: test_a -->
        ```python
        assert x == 1
        ```
    """,
    )
    blocks_a = [b for b in blocks if b.name == "test_a"]
    assert len(blocks_a) == 2

    code = compile_code_blocks(*blocks_a)
    assert code is not None
    exec(code)


def test_non_consecutive_multiple_separators(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_main -->
        ```python
        values = [1]
        ```

        <!-- name: test_other_1 -->
        ```python
        assert True
        ```

        <!-- name: test_other_2 -->
        ```python
        assert True
        ```

        <!-- name: test_main -->
        ```python
        values.append(2)
        ```

        <!-- name: test_other_3 -->
        ```python
        assert True
        ```

        <!-- name: test_main -->
        ```python
        assert values == [1, 2]
        ```
    """,
    )
    blocks_main = [b for b in blocks if b.name == "test_main"]
    assert len(blocks_main) == 3

    code = compile_code_blocks(*blocks_main)
    assert code is not None
    exec(code)


def test_non_consecutive_preserves_execution_order(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_order -->
        ```python
        result = []
        result.append("first")
        ```

        <!-- name: test_sep -->
        ```python
        pass
        ```

        <!-- name: test_order -->
        ```python
        result.append("second")
        ```

        <!-- name: test_sep2 -->
        ```python
        pass
        ```

        <!-- name: test_order -->
        ```python
        result.append("third")
        assert result == ["first", "second", "third"]
        ```
    """,
    )
    blocks_order = [b for b in blocks if b.name == "test_order"]
    code = compile_code_blocks(*blocks_order)
    assert code is not None
    exec(code)


def test_non_consecutive_class_definition(md_file):
    """Reproduces the exact scenario from issue #9."""
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_cls -->
        ```python
        class Foo:
            def __init__(self, value):
                self.value = value
        ```

        <!-- name: test_other -->
        ```python
        assert True
        ```

        <!-- name: test_cls -->
        ```python
        foo = Foo(42)
        assert foo.value == 42
        ```

        <!-- name: test_other2 -->
        ```python
        assert True
        ```

        <!-- name: test_cls -->
        ```python
        bar = Foo(99)
        assert foo.value + bar.value == 141
        ```
    """,
    )
    blocks_cls = [b for b in blocks if b.name == "test_cls"]
    assert len(blocks_cls) == 3

    code = compile_code_blocks(*blocks_cls)
    assert code is not None
    exec(code)


def test_no_duplicate_test_names(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_a -->
```python
x = 1
```

<!-- name: test_b -->
```python
assert True
```

<!-- name: test_a -->
```python
assert x == 1
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(passed=2)
    stdout = result.stdout.str()
    assert stdout.count("test_a PASSED") == 1
    assert stdout.count("test_b PASSED") == 1


def test_non_consecutive_integration(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_main -->
```python
data = {"key": "value"}
```

<!-- name: test_other -->
```python
assert 1 + 1 == 2
```

<!-- name: test_main -->
```python
data["key2"] = "value2"
```

<!-- name: test_another -->
```python
assert True
```

<!-- name: test_main -->
```python
assert data == {"key": "value", "key2": "value2"}
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(passed=3)


def test_non_consecutive_import_reuse(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_imp -->
```python
from collections import Counter
c = Counter()
```

<!-- name: test_sep -->
```python
assert True
```

<!-- name: test_imp -->
```python
c["a"] += 1
c["b"] += 2
assert c["a"] == 1
assert c["b"] == 2
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(passed=2)


def test_build_source_returns_source_and_path(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a -->
        ```python
        x = 1
        ```
    """,
    )
    result = _build_source(*blocks)
    assert result is not None
    source, path = result
    assert "x = 1" in source
    assert path.endswith("test.md")


def test_build_source_empty():
    assert _build_source() is None


def test_build_source_matches_compile(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a -->
        ```python
        x = 1
        ```

        <!-- name: test_a -->
        ```python
        assert x == 1
        ```
    """,
    )
    result = _build_source(*blocks)
    assert result is not None
    source, path = result
    code = compile(source=source, mode="exec", filename=path)
    exec(code)


def test_subprocess_basic(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub; subprocess: true -->
```python
assert 1 + 1 == 2
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(passed=1)


def test_subprocess_failure(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub_fail; subprocess: true -->
```python
assert False, "should fail"
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*AssertionError*Subprocess failed*"])


def test_subprocess_split(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub; subprocess: true -->
```python
x = 42
```

<!-- name: test_sub; subprocess: true -->
```python
assert x == 42
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(passed=1)


def test_subprocess_non_consecutive(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub; subprocess: true -->
```python
data = [1]
```

<!-- name: test_regular -->
```python
assert True
```

<!-- name: test_sub; subprocess: true -->
```python
data.append(2)
assert data == [1, 2]
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(passed=2)


def test_subprocess_interleaved_with_regular(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub; subprocess: true -->
```python
x = 10
```

<!-- name: test_reg -->
```python
y = 20
assert y == 20
```

<!-- name: test_sub; subprocess: true -->
```python
x += 5
assert x == 15
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(passed=2)


def test_subprocess_sigkill(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub_sigkill; subprocess: true -->
```python
import os, signal
os.kill(os.getpid(), signal.SIGKILL)
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*Subprocess failed (exit code -*"])


def test_subprocess_sigterm(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub_sigterm; subprocess: true -->
```python
import os, signal
os.kill(os.getpid(), signal.SIGTERM)
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*Subprocess failed (exit code -*"])


def test_subprocess_sys_exit(pytester):
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub_exit; subprocess: true -->
```python
import sys
sys.exit(42)
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*Subprocess failed (exit code 42)*"])

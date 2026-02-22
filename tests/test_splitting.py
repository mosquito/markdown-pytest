import textwrap

import pytest

from markdown_pytest import (
    _build_source, _collect_marks, _split_marks,
    compile_code_blocks, parse_code_blocks,
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


# --- _split_marks unit tests ---


def test_split_marks_single():
    assert _split_marks("xfail") == ["xfail"]


def test_split_marks_multiple():
    assert _split_marks("xfail, skip") == ["xfail", "skip"]


def test_split_marks_with_parens():
    assert _split_marks("xfail(raises=ZeroDivisionError)") == [
        "xfail(raises=ZeroDivisionError)",
    ]


def test_split_marks_mixed():
    assert _split_marks("xfail(raises=ValueError), skip") == [
        "xfail(raises=ValueError)",
        "skip",
    ]


def test_split_marks_empty():
    assert _split_marks("") == []


def test_split_marks_nested_parens():
    assert _split_marks("xfail(reason='a, b'), skip") == [
        "xfail(reason='a, b')",
        "skip",
    ]


# --- _collect_marks unit tests ---


def test_collect_marks_empty(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a -->
        ```python
        x = 1
        ```
    """,
    )
    assert _collect_marks(blocks) == ()


def test_collect_marks_xfail(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a; mark: xfail -->
        ```python
        x = 1
        ```
    """,
    )
    marks = _collect_marks(blocks)
    assert len(marks) == 1
    assert marks[0].name == "xfail"


def test_collect_marks_xfail_raises(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a; mark: xfail(raises=ZeroDivisionError) -->
        ```python
        1 / 0
        ```
    """,
    )
    marks = _collect_marks(blocks)
    assert len(marks) == 1
    assert marks[0].name == "xfail"
    assert marks[0].kwargs["raises"] == ZeroDivisionError


def test_collect_marks_from_split_blocks(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a; mark: xfail -->
        ```python
        x = 1
        ```

        <!-- name: test_a -->
        ```python
        assert x == 2
        ```
    """,
    )
    marks = _collect_marks(blocks)
    assert len(marks) == 1
    assert marks[0].name == "xfail"


def test_collect_marks_deduplicates(md_file):
    blocks = parse_blocks(
        md_file,
        """\
        <!-- name: test_a; mark: xfail -->
        ```python
        x = 1
        ```

        <!-- name: test_a; mark: xfail -->
        ```python
        assert x == 2
        ```
    """,
    )
    marks = _collect_marks(blocks)
    assert len(marks) == 1


# --- pytester integration tests for marks ---


def test_mark_xfail_raises_correct(pytester):
    """xfail(raises=X) passes when correct exception raised → XFAIL."""
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_xr; mark: xfail(raises=ZeroDivisionError) -->
```python
1 / 0
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(xfailed=1)


def test_mark_xfail_raises_wrong(pytester):
    """xfail(raises=X) fails when wrong exception → FAILED."""
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_xr; mark: xfail(raises=ZeroDivisionError) -->
```python
raise ValueError("wrong")
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(failed=1)


def test_mark_xfail_raises_no_exception(pytester):
    """xfail(raises=X) when no exception → XPASS."""
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_xr; mark: xfail(raises=ZeroDivisionError) -->
```python
x = 1
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    # non-strict xfail that passes → xpassed
    result.assert_outcomes(xpassed=1)


def test_mark_skip(pytester):
    """skip → test is skipped."""
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_s; mark: skip(reason="not needed") -->
```python
assert False
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(skipped=1)


def test_mark_xfail_simple(pytester):
    """xfail without args → XFAIL on failure."""
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_xf; mark: xfail -->
```python
assert False
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(xfailed=1)


def test_mark_multiple(pytester):
    """Multiple marks applied correctly."""
    pytester.makefile(
        ".md",
        test_doc="""\
<!--
    name: test_mm;
    mark: xfail;
    mark: strict
-->
```python
assert False
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    # xfail + strict custom marker → xfailed
    result.assert_outcomes(xfailed=1)


def test_mark_split_blocks(pytester):
    """Mark on first block applies to combined test."""
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sp; mark: xfail -->
```python
x = 1
```

<!-- name: test_sp -->
```python
assert x == 2
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(xfailed=1)


def test_mark_subprocess_xfail(pytester):
    """Mark with subprocess + xfail."""
    pytester.makefile(
        ".md",
        test_doc="""\
<!-- name: test_sub_xf; mark: xfail; subprocess: true -->
```python
assert False, "expected failure"
```
""",
    )
    result = pytester.runpytest_subprocess("-v")
    result.assert_outcomes(xfailed=1)

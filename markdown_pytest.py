import builtins
import inspect
import io
import os
import sys

from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT
from contextlib import suppress
from pathlib import Path
from types import CodeType
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    NamedTuple,
    Optional,
    TextIO,
    Tuple,
)

import pytest


_ASYNC_PREFIX = "async "


class CodeBlock(NamedTuple):
    start_line: int
    lines: Tuple[str, ...]
    arguments: Tuple[Tuple[str, str], ...]
    path: str
    name: str
    is_async: bool = False

    @property
    def end_line(self) -> int:
        return self.start_line + len(self.lines)


COMMENT_BRACKETS = ("<!--", "-->")


LineType = Tuple[int, str]


class LinesIterator:
    lines: Tuple[LineType, ...]

    def __init__(self, lines: Iterable[str]) -> None:
        self.lines = tuple(
            (i, line)
            for i, line in enumerate(
                (line.rstrip() for line in lines),
            )
        )
        self.index = 0

    @classmethod
    def from_fp(cls, fp: TextIO) -> "LinesIterator":
        return cls(fp.readlines())

    @classmethod
    def from_file(cls, filename: str) -> "LinesIterator":
        with open(filename, "r") as fp:
            return cls.from_fp(fp)

    def get_relative(self, index: int) -> LineType:
        return self.lines[self.index + index]

    def is_last_line(self) -> bool:
        return self.index >= len(self.lines)

    def next(self) -> LineType:
        lineno, line = self.get_relative(0)
        self.index += 1
        return lineno, line

    def seek_relative(self, index: int) -> None:
        self.index += index

    def reverse_iterator(
        self,
        start_from: int = 0,
    ) -> Iterator[LineType]:
        for i in range(start_from, self.index):
            yield self.get_relative(-i - 1)

    def __iter__(self) -> "LinesIterator":
        return self

    def __next__(self) -> LineType:
        try:
            return self.next()
        except IndexError:
            raise StopIteration


def parse_arguments(line_iterator: LinesIterator) -> Dict[str, str]:

    outside_comment = inside_comment = False
    index = line_iterator.index
    # Checking if the code block is outside of the comment block
    for lineno, line in line_iterator.reverse_iterator(1):
        if not line.strip():
            continue
        if line.strip().endswith(COMMENT_BRACKETS[1]):
            outside_comment = True
        break

    # Checking if the code block is inside of the comment block
    if not outside_comment:
        for lineno, line in line_iterator:
            if not line.strip():
                continue
            if line.strip().endswith(COMMENT_BRACKETS[0]):
                return {}
            elif line.strip().endswith(COMMENT_BRACKETS[1]):
                inside_comment = True
                line_iterator.seek_relative(1)
                break

    if not outside_comment and not inside_comment:
        return {}

    lines = []
    reverse_iterator = line_iterator.reverse_iterator(1)
    for lineno, line in reverse_iterator:
        if line.strip().startswith("```"):
            for _, line in reverse_iterator:
                if line.strip().startswith("```"):
                    break
            continue
        lines.append(line)
        if line.strip().startswith(COMMENT_BRACKETS[0]):
            break

    # Restore the iterator (due to inside comment forward iterations)
    line_iterator.index = index

    if not lines:
        return {}

    lines = lines[::-1]
    result = {}
    args = "".join(
        "".join(lines)
        .strip()[len(COMMENT_BRACKETS[0]) : -len(COMMENT_BRACKETS[1]) + 1]
        .strip("-")
        .strip()
        .splitlines(),
    ).split(";")

    for arg in args:
        if ":" not in arg:
            continue

        key, value = arg.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in result:
            result[key] = f"{result[key]}, {value}"
        else:
            result[key] = value

    return result


def parse_code_blocks(fspath: str) -> Iterator[CodeBlock]:
    line_iterator = LinesIterator.from_file(fspath)

    for lineno, line in line_iterator:
        stripped = line.lstrip()
        if not stripped.startswith("```"):
            continue

        # Count the leading backtick run (fence length)
        backtick_count = len(stripped) - len(stripped.lstrip("`"))
        info_string = stripped[backtick_count:].strip()

        info_words = info_string.split()
        if not info_words or info_words[0] != "python":
            # Non-Python fenced block (```bash, ```json, bare ```, etc.)
            # Skip to the closing fence
            closing_fence = "`" * backtick_count
            for lineno, line in line_iterator:
                if line.strip() == closing_fence:
                    break
            continue

        indent = len(line) - len(stripped)
        end_of_block = (" " * indent) + ("`" * backtick_count)

        arguments = parse_arguments(line_iterator)

        # the next line after ```python
        start_lineno = lineno + 1
        code_lines = []

        for lineno, line in line_iterator:
            if line.startswith(end_of_block):
                break
            code_lines.append(line[indent:])

        if not arguments or "name" not in arguments:
            continue

        case = arguments.get("case")
        if case is not None:
            start_lineno -= 1
            # indent test case lines
            code_lines = [f"    {code_line}" for code_line in code_lines]
            code_lines.insert(
                0,
                "with __markdown_pytest_subtests_fixture.test("
                f"msg='{case} line={start_lineno}'):",
            )

        name = arguments.pop("name")
        is_async = False
        if name.startswith(_ASYNC_PREFIX):
            is_async = True
            name = name.removeprefix(_ASYNC_PREFIX)

        block = CodeBlock(
            start_line=start_lineno,
            lines=tuple(code_lines),
            arguments=tuple(arguments.items()),
            path=str(fspath),
            name=name,
            is_async=is_async,
        )

        yield block


def _build_source(
    *blocks: CodeBlock,
) -> Optional[Tuple[str, str]]:
    sorted_blocks = sorted(blocks, key=lambda x: x.start_line)
    if not sorted_blocks:
        return None
    lines = [""] * sorted_blocks[-1].end_line
    path = sorted_blocks[0].path
    for block in sorted_blocks:
        lines[block.start_line : block.end_line] = block.lines
    return "\n".join(lines), path


def compile_code_blocks(
    *blocks: CodeBlock,
    is_async: bool = False,
) -> Optional[CodeType]:
    result = _build_source(*blocks)
    if result is None:
        return None
    source, path = result
    flags = PyCF_ALLOW_TOP_LEVEL_AWAIT if is_async else 0
    return compile(
        source=source, mode="exec", filename=path, flags=flags,
    )


def _collect_fixture_names(
    blocks: Iterable[CodeBlock],
) -> Tuple[str, ...]:
    names: list[str] = []
    for block in blocks:
        arguments = dict(block.arguments)
        fixtures_str = arguments.get("fixtures", "")
        for name in fixtures_str.split(","):
            name = name.strip()
            if name:
                names.append(name)
    return tuple(dict.fromkeys(names))


def _split_marks(value: str) -> list[str]:
    result: list[str] = []
    depth = 0
    current: list[str] = []
    for char in value:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                result.append(part)
            current = []
            continue
        current.append(char)
    part = "".join(current).strip()
    if part:
        result.append(part)
    return result


def _collect_marks(
    blocks: Iterable[CodeBlock],
) -> Tuple[Any, ...]:
    raw_parts: list[str] = []
    for block in blocks:
        arguments = dict(block.arguments)
        mark_str = arguments.get("mark", "").strip()
        if not mark_str:
            continue
        raw_parts.extend(_split_marks(mark_str))

    marks: list[Any] = []
    ns: Dict[str, Any] = {**vars(builtins), "pytest": pytest}
    for part in dict.fromkeys(raw_parts):
        marks.append(eval(f"pytest.mark.{part}", ns))
    return tuple(marks)


def _optionflags(example: Any) -> int:
    flags = 0
    for flag, value in example.options.items():
        if value:
            flags |= flag
    return flags


async def _run_async_doctest(test: Any, out: Any) -> int:
    import doctest
    import traceback as _tb

    checker = doctest.OutputChecker()
    failures = 0

    for example in test.examples:
        if example.options.get(doctest.SKIP, False):
            continue

        capture = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = capture
        exc_info = None

        try:
            code = compile(
                example.source,
                test.filename or "<doctest>",
                "single",
                PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
            result = eval(code, test.globs)
            if inspect.isawaitable(result):
                await result
        except SystemExit:
            sys.stdout = old_stdout
            raise
        except BaseException:
            exc_info = sys.exc_info()
        finally:
            sys.stdout = old_stdout

        actual = capture.getvalue()

        if exc_info is not None:
            exc_type, exc_val, _ = exc_info
            if example.exc_msg is not None:
                exc_str = "".join(_tb.format_exception_only(exc_type, exc_val))
                if checker.check_output(example.exc_msg, exc_str, _optionflags(example)):
                    continue
            failures += 1
            tb_str = "".join(_tb.format_exception(*exc_info))
            out(
                f"Failed example:\n    {example.source.rstrip()}\n"
                "Exception raised:\n"
                + "".join(f"    {line}" for line in tb_str.splitlines(keepends=True))
                + "\n"
            )
            continue

        if not example.want:
            continue

        if checker.check_output(example.want, actual, _optionflags(example)):
            continue

        failures += 1
        out(
            f"Failed example:\n    {example.source.rstrip()}\n"
            "Expected:\n"
            + "".join(f"    {line}" for line in example.want.splitlines(keepends=True))
            + "Got:\n"
            + "".join(f"    {line}" for line in actual.splitlines(keepends=True))
            + "\n"
        )

    return failures


def _make_async_doctest_caller(
    source: str,
    path: str,
    fixture_names: Tuple[str, ...],
) -> Any:
    import doctest

    all_names = tuple(dict.fromkeys((*fixture_names, "subtests")))

    async def caller(**kwargs: Any) -> None:
        kwargs.pop("subtests")
        globs: Dict[str, Any] = dict(kwargs)

        parser = doctest.DocTestParser()
        test = parser.get_doctest(source, globs, path, path, 0)

        out_buf = io.StringIO()
        failures = await _run_async_doctest(test, out_buf.write)

        if failures:
            raise AssertionError(out_buf.getvalue())

    params = [
        inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY)
        for name in all_names
    ]
    caller.__signature__ = inspect.Signature(parameters=params)  # type: ignore
    return caller


def _make_doctest_caller(
    source: str,
    path: str,
    fixture_names: Tuple[str, ...],
) -> Any:
    import doctest

    all_names = tuple(dict.fromkeys((*fixture_names, "subtests")))

    def caller(**kwargs: Any) -> None:
        kwargs.pop("subtests")
        globs: Dict[str, Any] = dict(kwargs)

        parser = doctest.DocTestParser()
        test = parser.get_doctest(source, globs, path, path, 0)

        out_buf = io.StringIO()
        runner = doctest.DocTestRunner(verbose=False)
        results = runner.run(test, out=out_buf.write)

        if results.failed:
            raise AssertionError(out_buf.getvalue())

    params = [
        inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY)
        for name in all_names
    ]
    caller.__signature__ = inspect.Signature(parameters=params)  # type: ignore
    return caller


def _make_caller(
    code: CodeType,
    fixture_names: Tuple[str, ...],
    is_async: bool = False,
) -> Any:
    all_names = tuple(dict.fromkeys((*fixture_names, "subtests")))

    if is_async:
        async def caller(**kwargs: Any) -> None:
            subtests = kwargs.pop("subtests")
            ns: Dict[str, Any] = dict(
                __markdown_pytest_subtests_fixture=subtests,
            )
            ns.update(kwargs)
            result = eval(code, ns)
            if inspect.iscoroutine(result):
                await result
    else:
        def caller(**kwargs: Any) -> None:
            subtests = kwargs.pop("subtests")
            ns: Dict[str, Any] = dict(
                __markdown_pytest_subtests_fixture=subtests,
            )
            ns.update(kwargs)
            eval(code, ns)

    params = [
        inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY)
        for name in all_names
    ]
    caller.__signature__ = inspect.Signature(parameters=params)  # type: ignore
    return caller


class MDModule(pytest.Module):
    @staticmethod
    def subprocess_caller(
        source: str, path: str, is_async: bool = False,
    ) -> None:
        import subprocess
        import sys
        import tempfile
        import textwrap

        if is_async:
            source = (
                "import asyncio\n"
                "async def __amain():\n"
                f"{textwrap.indent(source, '    ')}\n"
                "asyncio.run(__amain())\n"
            )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False,
        ) as f:
            f.write(source)
            tmp = f.name

        try:
            result = subprocess.run(
                [sys.executable, tmp],
                capture_output=True, text=True,
            )
        finally:
            os.unlink(tmp)

        if result.returncode != 0:
            raise AssertionError(
                f"Subprocess failed (exit code {result.returncode}):"
                f"\n{result.stdout}\n{result.stderr}",
            )

    def collect(self) -> Iterable[pytest.Function]:
        from functools import partial

        test_prefix = self.config.getoption("--md-prefix")

        blocks_by_name: Dict[str, list] = {}
        for block in parse_code_blocks(str(self.path)):
            if not block.name.startswith(test_prefix):
                continue
            blocks_by_name.setdefault(block.name, []).append(block)

        for test_name, blocks in blocks_by_name.items():
            use_subprocess = any(
                dict(b.arguments).get("subprocess") == "true"
                for b in blocks
            )
            use_repl = any(
                dict(b.arguments).get("repl") == "true"
                for b in blocks
            )
            is_async = any(b.is_async for b in blocks)
            marks = _collect_marks(blocks)

            if use_subprocess:
                result = _build_source(*blocks)
                if result is None:
                    continue
                source, path = result
                item = pytest.Function.from_parent(
                    name=test_name,
                    parent=self,
                    callobj=partial(
                        self.subprocess_caller, source, path, is_async,
                    ),
                )
            elif use_repl:
                result = _build_source(*blocks)
                if result is None:
                    continue
                source, path = result
                fixture_names = _collect_fixture_names(blocks)
                caller_fn = (
                    _make_async_doctest_caller if is_async
                    else _make_doctest_caller
                )
                item = pytest.Function.from_parent(
                    name=test_name,
                    parent=self,
                    callobj=caller_fn(source, path, fixture_names),
                )
            else:
                code = compile_code_blocks(*blocks, is_async=is_async)
                if code is None:
                    continue

                fixture_names = _collect_fixture_names(blocks)

                item = pytest.Function.from_parent(
                    name=test_name,
                    parent=self,
                    callobj=_make_caller(
                        code, fixture_names, is_async=is_async,
                    ),
                )

            for mark in marks:
                item.add_marker(mark)
            if is_async and not use_subprocess:
                with suppress(ImportError):
                    from pytest_asyncio.plugin import PytestAsyncioFunction
                    item.add_marker(pytest.mark.asyncio)
                    subclass = PytestAsyncioFunction.item_subclass_for(item)
                    if subclass is not None:
                        item = subclass._from_function(item)
            yield item


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--md-prefix",
        default="test",
        help="Markdown test code-block prefix from comment",
    )


@pytest.hookimpl(trylast=True)
def pytest_collect_file(
    file_path: Path,
    parent: pytest.Collector,
) -> Optional[MDModule]:
    if file_path.suffix.lower() not in (".md", ".markdown"):
        return None
    return MDModule.from_parent(parent=parent, path=file_path)

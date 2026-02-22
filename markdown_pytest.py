import inspect

from pathlib import Path
from types import CodeType
from typing import (
    Any, Dict, Iterable, Iterator, NamedTuple,
    Optional, TextIO, Tuple,
)

import pytest


class CodeBlock(NamedTuple):
    start_line: int
    lines: Tuple[str, ...]
    arguments: Tuple[Tuple[str, str], ...]
    path: str
    name: str

    @property
    def end_line(self) -> int:
        return self.start_line + len(self.lines)


COMMENT_BRACKETS = ("<!--", "-->")


LineType = Tuple[int, str]


class LinesIterator:
    lines: Tuple[LineType, ...]

    def __init__(self, lines: Iterable[str]) -> None:
        self.lines = tuple(
            (i, line) for i, line in enumerate(
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
        self, start_from: int = 0,
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
        "".join(lines).strip()[
            len(COMMENT_BRACKETS[0]):-len(COMMENT_BRACKETS[1]) + 1
        ].strip("-").strip().splitlines(),
    ).split(";")

    for arg in args:
        if ":" not in arg:
            continue

        key, value = arg.split(":", 1)
        result[key.strip()] = value.strip()

    return result


def parse_code_blocks(fspath: str) -> Iterator[CodeBlock]:
    line_iterator = LinesIterator.from_file(fspath)

    for lineno, line in line_iterator:
        if (
            line.rstrip().endswith("```") and
            line.lstrip().startswith("```")
        ):
            # skip all blocks without '```python`
            end_of_block = "`" * line.count("`")
            try:
                lineno, line = line_iterator.next()
            except IndexError:
                return

            for lineno, line in line_iterator:
                if line.rstrip() == end_of_block:
                    break

        if not line.endswith("```python"):
            continue

        indent = line.rstrip().count(" ")
        end_of_block = (" " * indent) + ("`" * line.count("`"))

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
                0, "with __markdown_pytest_subtests_fixture.test("
                   f"msg='{case} line={start_lineno}'):",
            )

        block = CodeBlock(
            start_line=start_lineno,
            lines=tuple(code_lines),
            arguments=tuple(arguments.items()),
            path=str(fspath),
            name=arguments.pop("name"),
        )

        yield block


def compile_code_blocks(*blocks: CodeBlock) -> Optional[CodeType]:
    sorted_blocks = sorted(blocks, key=lambda x: x.start_line)
    if not sorted_blocks:
        return None
    lines = [""] * sorted_blocks[-1].end_line
    path = sorted_blocks[0].path
    for block in sorted_blocks:
        lines[block.start_line:block.end_line] = block.lines
    return compile(source="\n".join(lines), mode="exec", filename=path)


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


def _make_caller(
    code: CodeType, fixture_names: Tuple[str, ...],
) -> Any:
    all_names = tuple(dict.fromkeys((*fixture_names, "subtests")))

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

    def collect(self) -> Iterable[pytest.Function]:
        test_prefix = self.config.getoption("--md-prefix")

        blocks_by_name: Dict[str, list] = {}
        for block in parse_code_blocks(str(self.fspath)):
            if not block.name.startswith(test_prefix):
                continue
            blocks_by_name.setdefault(block.name, []).append(block)

        for test_name, blocks in blocks_by_name.items():
            code = compile_code_blocks(*blocks)
            if code is None:
                continue

            fixture_names = _collect_fixture_names(blocks)

            yield pytest.Function.from_parent(
                name=test_name,
                parent=self,
                callobj=_make_caller(code, fixture_names),
            )


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--md-prefix", default="test",
        help="Markdown test code-block prefix from comment",
    )


@pytest.hookimpl(trylast=True)
def pytest_collect_file(
    path: Any, parent: pytest.Collector,
) -> Optional[MDModule]:
    if path.ext.lower() not in (".md", ".markdown"):
        return None
    return MDModule.from_parent(parent=parent, path=Path(path))

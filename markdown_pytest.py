from itertools import groupby
from pathlib import Path
from types import CodeType
from typing import Iterable, Iterator, Mapping, NamedTuple, Optional, Tuple

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


def parse_code_blocks(fspath) -> Iterator[CodeBlock]:
    with open(fspath, "r") as fp:
        lines = list(enumerate(fp.read().splitlines()))
        index = -1

        def parse_arguments(lines: Iterable[str]) -> Mapping[str, str]:
            result = {}
            if not lines:
                return result

            args = "".join(
                "".join(lines).strip()[5:-3].splitlines(),
            ).split(";")

            for arg in args:
                if ":" not in arg:
                    continue

                key, value = arg.split(":", 1)
                result[key.strip()] = value.strip()

            return result

        while index < len(lines):
            index += 1

            if index > (len(lines) - 1):
                return

            lineno, line = lines[index]

            if not line.rstrip().endswith("```python"):
                continue

            if index > 0 and lines[index - 1][1].endswith("-->"):
                arguments_lines = []
                for i in range(index - 1, -1, -1):
                    arguments_lines.append(lines[i][1].strip("-"))
                    if lines[i][1].startswith("<!--"):
                        break

                arguments = parse_arguments(arguments_lines[::-1])
            else:
                arguments = {}

            # the next line after ```python
            start_lineno = lineno + 1
            code_lines = []

            while True:
                index += 1
                lineno, line = lines[index]

                if line.rstrip().startswith("```"):
                    break

                code_lines.append(line)

            if not arguments or "name" not in arguments:
                continue

            yield CodeBlock(
                start_line=start_lineno,
                lines=tuple(code_lines),
                arguments=tuple(arguments.items()),
                path=str(fspath),
                name=arguments.pop("name"),
            )


class MDTestItem(pytest.Item):
    def __init__(self, name: str, parent: "MDModule", code: CodeType):
        super().__init__(name=name, parent=parent)
        self.module = code

    def runtest(self) -> None:
        exec(self.module, {"__name__": "markdown-pytest"})


def compile_code_blocks(*blocks: CodeBlock) -> Optional[CodeType]:
    blocks = sorted(blocks, key=lambda x: x.start_line)
    if not blocks:
        return None
    lines = [""] * blocks[-1].end_line
    path = blocks[0].path
    for block in blocks:
        lines[block.start_line:block.end_line] = block.lines
    return compile(source="\n".join(lines), mode="exec", filename=path)


class MDModule(pytest.Module):
    def collect(self) -> Iterable["MDTestItem"]:
        test_prefix = self.config.getoption("--md-prefix")

        for test_name, blocks in groupby(
            parse_code_blocks(self.fspath),
            key=lambda x: x.name,
        ):
            if not test_name.startswith(test_prefix):
                continue

            blocks = list(blocks)
            code = compile_code_blocks(*blocks)
            if code is None:
                continue

            yield MDTestItem.from_parent(name=test_name, parent=self, code=code)


def pytest_addoption(parser):
    parser.addoption(
        "--md-prefix", default="test",
        help="Markdown test code-block prefix from comment",
    )


@pytest.hookimpl(trylast=True)
def pytest_collect_file(path, parent: pytest.Collector) -> Optional[MDModule]:
    if path.ext.lower() not in (".md", ".markdown"):
        return None
    return MDModule.from_parent(parent=parent, path=Path(path))

from io import StringIO
from pathlib import Path
from types import CodeType
from typing import IO, Iterable, Iterator, NamedTuple, Optional, Tuple

import py
import pytest


class CodeBlock(NamedTuple):
    start_line: int
    syntax: Optional[str]
    lines: Tuple[str, ...]

    @property
    def end_line(self) -> int:
        return self.start_line + len(self.lines)


def parse_code_blocks(fp: IO[str]) -> Iterator[CodeBlock]:
    fp.seek(0)

    lineno = 0

    def make_code_block(start_lineno: int, syntax: str) -> CodeBlock:
        nonlocal lineno

        lines = []
        syntax = syntax.strip()
        for code_line in fp:
            if code_line.startswith("```"):
                lineno += 1
                return CodeBlock(
                    start_line=start_lineno,
                    lines=tuple(lines),
                    syntax=syntax if syntax != "" else None,
                )
            lines.append(code_line)
            lineno += 1

    for line in fp:
        if line.startswith("```"):
            yield make_code_block(lineno + 1, syntax=line.lstrip("`"))
        lineno += 1


class MDTestItem(pytest.Item):
    def __init__(self, name: str, parent: "MDModule", code: CodeType):
        super().__init__(name=name, parent=parent)
        self.module = code

    def runtest(self) -> None:
        exec(self.module, {"__name__": "markdown-pytest"})


class MDModule(pytest.Module):
    def collect(self) -> Iterable["MDTestItem"]:
        with open(self.fspath, "r") as fp:
            for code_block in parse_code_blocks(fp):
                if code_block.syntax != "python":
                    continue

                with StringIO() as code_fp:
                    code_fp.write("\n" * code_block.start_line)
                    for line in code_block.lines:
                        if line.strip().startswith("# noqa"):
                            break
                        code_fp.write(line)

                    test_name = (
                        f"{code_block.start_line}-{code_block.end_line}"
                    )

                    yield MDTestItem.from_parent(
                        name=f"line[{test_name}]",
                        parent=self,
                        code=compile(
                            source=code_fp.getvalue(), mode="exec",
                            filename=self.fspath,
                        ),
                    )


@pytest.hookimpl(trylast=True)
def pytest_collect_file(
    path: py.path.local, parent: pytest.Collector,
) -> Optional[MDModule]:
    if path.ext.lower() not in (".md", ".markdown"):
        return None

    return MDModule.from_parent(parent=parent, path=Path(path))

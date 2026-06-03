Async tests
===========

Basic async test using top-level `await`:

<!-- name: async test_async_basic -->
```python
import asyncio
await asyncio.sleep(0)
assert True
```

Async test without await:

<!-- name: async test_async_basic_no_await -->
```python
assert True
```

Async test with `await` returning a value:

<!-- name: async test_async_await_value -->
```python
import asyncio

async def produce() -> int:
    return 42

assert await produce() == 42
```

Async test split across multiple blocks (only first block needs `async`
prefix — async-ness is inherited by all blocks with the same name):

<!-- name: async test_async_split -->
```python
import asyncio

async def test():
    return True

assert await test()
```

<!-- name: test_async_split -->
```python
assert await test()
```

Async test combined with a pytest fixture:

<!-- name: async test_async_fixture; fixtures: tmp_path -->
```python
import asyncio

async def write_file(path):
    path.write_text("test")

path = tmp_path / "async.txt"
await write_file(path)
assert path.read_text() == "test"
```

Async test combined with an async pytest fixture:

<!-- name: async test_async_async_fixture; fixtures: async_fixture -->
```python
import asyncio

assert async_fixture is asyncio.get_event_loop()
```

Async test with subtests (`case:`):

<!-- name: async test_async_cases -->
```python
import asyncio

async def add(a, b):
    await asyncio.sleep(0)
    return a + b
```

<!-- name: test_async_cases; case: positive -->
```python
assert await add(1, 2) == 3
```

<!-- name: test_async_cases; case: negative -->
```python
assert await add(-1, -2) == -3
```

Async test in subprocess mode — the source is wrapped in
`async def __amain(): ...; asyncio.run(__amain())` before being launched
in a separate Python process:

<!-- name: async test_async_subprocess; subprocess: true -->
```python
import asyncio
await asyncio.sleep(0)
assert 2 + 2 == 4
```

Async subprocess split across blocks:

<!-- name: async test_async_subprocess_split; subprocess: true -->
```python
import asyncio

async def calc():
    await asyncio.sleep(0)
    return 7
```

<!-- name: test_async_subprocess_split; subprocess: true -->
```python
assert await calc() == 7
```

Async test combined with marks — `xfail` triggers when the awaited
coroutine raises:

<!-- name: async test_async_xfail; mark: xfail(raises=ZeroDivisionError) -->
```python
import asyncio

async def boom():
    await asyncio.sleep(0)
    return 1 / 0

await boom()
```

# Repl Tests

## Arithmetic

<!-- name: test_repl_arithmetic; repl: true -->
```python
>>> 1 + 1
2
>>> 2 ** 8
256
```

## Print output

<!-- name: test_repl_print; repl: true -->
```python
>>> print("hello, world")
hello, world
>>> name = "pytest"
>>> print(f"hello, {name}")
hello, pytest
```

## List repr

<!-- name: test_repl_list; repl: true -->
```python
>>> items = [1, 2, 3]
>>> items.append(4)
>>> items
[1, 2, 3, 4]
```

## Async

<!-- name: async test_repl_async; repl: true -->
```python
>>> import asyncio
>>> await asyncio.sleep(0)
>>> 1 + 1
2
```

## Async with return value

<!-- name: async test_repl_async_return; repl: true -->
```python
>>> import asyncio
>>> async def double(x):
...     await asyncio.sleep(0)
...     return x * 2
>>> await double(21)
42
```

## Split blocks

<!-- name: test_repl_split; repl: true -->
```python
>>> x = 42
```

<!-- name: test_repl_split; repl: true -->
```python
>>> x
42
```

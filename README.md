markdown-pytest
===============

A simple module to test your documentation examples with pytest.

Markdown:

```markdown
    ```python
    assert True
    ```
```

Will be shown as:

```python
assert False
```

You can use the special value `__name__` to check to separate the run example 
and the test code.

Markdown:

```markdown
    ```python
    if __name__ == '__main__':
        exit(0)
    if __name__ == 'markdown-pytest':
        assert True
    ```
```

Will be shown as:

```python
if __name__ == '__main__':
    exit(0)
if __name__ == 'markdown-pytest':
    assert True
```

Code after the `# noqa` comment will not be executed.

```markdown
    ```python
    # noqa
    from universe import antigravity, WrongPlanet

    try:
        antigravity()
    except WrongPlanet:
        print("You are on the wrong planet.")
        exit(1)
    ```
```

Will be shown as:

```python
# noqa
from universe import antigravity, WrongPlanet

try:
    antigravity()
except WrongPlanet:
    print("You are on the wrong planet.")
    exit(1)
```

This README.md file might be tested like this:

```bash
$ poetry run pytest -sxv README.md                                                                                                                                    17:20:29 master
=============== test session starts ===============
plugins: md-0.1.0
collected 3 items

README.md::line[16-17] PASSED
README.md::line[36-40] PASSED
README.md::line[60-68] PASSED
```

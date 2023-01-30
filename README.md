markdown-pytest
===============

A simple module to test your documentation examples with pytest.

Markdown:

```markdown
<!--- name: test_assert_true -->
&#96;&#96;&#96;python
assert True
&#96;&#96;&#96;
```

Will be shown as:

<!--- name: test_assert_true -->
```python
assert True
```

You can split test to the multiple blocks with the same test name:

Markdown:

```markdown
Import example:

<!--- name: test_example -->
&#96;&#96;&#96;python
from itertools import chain
&#96;&#96;&#96;

Some chain usage example:

<!--- name: test_example -->
&#96;&#96;&#96;python
assert list(chain(range(2), range(2))) == [0, 1, 0, 1]
&#96;&#96;&#96;
```

Will be shown as:

Import example:

<!--- name: test_example -->
```python
from itertools import chain
```

Some chain usage example:

<!--- name: test_example -->
```python
assert list(chain(range(2), range(2))) == [0, 1, 0, 1]
```

Code without `&#60;!--- name: test_name --&#62;` comment will not be executed.

```markdown
&#96;&#96;&#96;python
from universe import antigravity, WrongPlanet

try:
    antigravity()
except WrongPlanet:
    print("You are on the wrong planet.")
    exit(1)
&#96;&#96;&#96;
```

Will be shown as:

```python
from universe import antigravity, WrongPlanet

try:
    antigravity()
except WrongPlanet:
    print("You are on the wrong planet.")
    exit(1)
```

This README.md file might be tested like this:

```bash
$ pytest -v README.md
======================= test session starts =======================
platform darwin -- Python 3.10.2, pytest-7.2.0, pluggy-1.0.0
plugins: markdown-pytest-0.1.0
collected 2 items

README.md::test_assert_true PASSED                                                                                                                                                                                                     [ 50%]
README.md::test_example PASSED
```

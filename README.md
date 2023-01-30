markdown-pytest
===============

Pytest plugin for running tests directly from Markdown files.

Markdown:

````markdown
<!-- name: test_assert_true -->
```python
assert True
```
````

<details>
<summary>Will be shown as</summary>

<!-- name: test_assert_true -->
```python
assert True
```

</details>

This module parsed code by these rules:

* Code without `<!-- name: test_name -->` comment will not be executed.
* Allowed two or three dashes in the comment symbols
* Code blocks with same names will be merged in one code and executed once

Code split
----------

You can split test to the multiple blocks with the same test name:

Markdown:

````markdown
This block performs import:

<!-- name: test_example -->
```python
from itertools import chain
```

`chain` usage example:

<!-- name: test_example -->
```python
assert list(chain(range(2), range(2))) == [0, 1, 0, 1]
```
````

<details>
<summary>Will be shown as</summary>

This block performs import:

<!-- name: test_example -->
```python
from itertools import chain
```

`chain` usage example:

<!-- name: test_example -->
```python
assert list(chain(range(2), range(2))) == [0, 1, 0, 1]
```

</details>

Fictional Code Examples
-----------------------

Code without `<!-- name: test_name -->` comment will not be executed.

````markdown
```python
from universe import antigravity, WrongPlanet

try:
    antigravity()
except WrongPlanet:
    print("You are on the wrong planet.")
    exit(1)
```
````

<details>
<summary>Will be shown as</summary>

```python
from universe import antigravity, WrongPlanet

try:
    antigravity()
except WrongPlanet:
    print("You are on the wrong planet.")
    exit(1)
```
</details>

Usage example
-------------

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

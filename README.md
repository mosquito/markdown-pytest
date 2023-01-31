markdown-pytest
===============

The `markdown-pytest` plugin is a `pytest` plugin that allows you to run tests
directly from Markdown files.

With this plugin, you can write your tests inside Markdown files, making it
easy to read, understand and maintain your documentation samples.
The tests are executed just like any other Pytest tests.

Sample of markdown file content:

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

Restrictions
------------

Since there is no way to add attributes to a block of code in markdown, this 
module only runs those tests that are marked with a special comment.

The general format of this comment is as follows: parts separated by semicolons
are a colon separated key-value pairs, the last semicolon is optional,
and parts not containing a colon are ignored.

Example:

```
<!-- key1: value1; key2: value2 -->
```

This comment should be placed right before the block of code, namely the 
line ````python`.

The `name` key is required, and blocks that do not contain it will be ignored.

Common rules
------------

This module parsing code in files by these rules:

* Code without `<!-- name: test_name -->` comment will not be executed.
* Allowed two or three dashes in the comment symbols
* Code blocks with same names will be merged in one code and executed once
* The optional comment parameter `case` will execute the block as a subtest.

Code split
----------

You can split a test into multiple blocks with the same test name:

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

subtests support
----------------

Of course, you can break tests into subtests by simply adding `case: case_name` 
to the markdown comment.

````markdown
<!-- name: test_counter -->
```python
from collections import Counter
```

<!-- 
    name: test_counter;
    case: initialize_counter
-->
```python
counter = Counter()
```

<!-- 
    name: test_counter;
    case: assign_counter_value
-->
```python
counter["foo"] += 1

assert counter["foo"] == 1
```
````

<details>
<summary>Will be shown as</summary>

<!-- name: test_counter -->
```python
from collections import Counter
```

<!-- 
    name: test_counter;
    case: initialize_counter
-->
```python
counter = Counter()
```

<!-- 
    name: test_counter;
    case: assign_counter_value
-->
```python
counter["foo"] += 1

assert counter["foo"] == 1
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

README.md::test_assert_true PASSED                                                                                                                                                                             [ 33%]
README.md::test_example PASSED                                                                                                                                                                                 [ 66%]
README.md::test_counter SUBPASS                                                                                                                                                                                [100%]
README.md::test_counter SUBPASS                                                                                                                                                                                [100%]
README.md::test_counter PASSED
```



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
and parts not containing a colon bill be ignored.

Example:

```markdown
<!-- key1: value1; key2: value2 -->
```

Multiline example:

```markdown
<!-- 
    key1: value1; 
    key2: value2;
-->
```

This comment should be placed right before the block of code, exactly upper 
the backticks, for example: 

````
<!-- name: test_name -->
```python
```
````

The `name` key is required, and blocks that do not contain it will be ignored.

Some Markdown parsers support two or three dashes around comments, this module 
supports both variants. The `case` parameter is optional and might be used for
subtests, see "Code split" section.

Additionally, a code block can be put inside the comment block to hide some 
initialization from the readers.

````markdown
<!-- name: test_name
```python
init_some_variable = 123
```
-->
```python
assert init_some_variable == 123
```
````

Common parsing rules
--------------------

This module uses its own, very simple Markdown parser, which only supports code 
block parsing. In general, the parsing behavior of a file follows the following 
rules:

* Code without `<!-- name: test_name -->` comment will not be executed.
* Allowed two or three dashes in the comment symbols

  For example following line will be parsed identically:

  ````markdown
  <!--  name: test_name -->
  <!--- name: test_name --->
  <!--  name: test_name --->
  <!--- name: test_name -->
  ````

* Code blocks with same names will be merged in one code and executed once
* The optional comment parameter `case` will execute the block as a subtest.
* Indented code blocks will be shifted left.
  
  For example:

  ````markdown
      <!-- name: test_name -->
      ```python
      assert True
      ```
  ````

  Is the same of:

  ````markdown
  <!-- name: test_name -->
  ```python
  assert True
  ```
  ````

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

Fixtures support
----------------

You can request pytest fixtures by adding `fixtures: fixture1, fixture2` to the
markdown comment. The fixtures will be available as variables in the code block.

Single fixture:

````markdown
<!-- name: test_with_tmp_path; fixtures: tmp_path -->
```python
p = tmp_path / "hello.txt"
p.write_text("hello")
assert p.read_text() == "hello"
```
````

Multiple fixtures:

````markdown
<!-- name: test_with_fixtures; fixtures: tmp_path, monkeypatch -->
```python
import os
monkeypatch.setenv("DATA_DIR", str(tmp_path))
assert os.environ["DATA_DIR"] == str(tmp_path)
```
````

Split blocks with fixtures — only the first block needs the `fixtures:` declaration:

````markdown
<!-- name: test_split_fixtures; fixtures: tmp_path -->
```python
p = tmp_path / "data.txt"
p.write_text("hello")
```

<!-- name: test_split_fixtures -->
```python
assert p.read_text() == "hello"
```
````

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

This README.md file can be tested like this:

```bash
$ pytest -v README.md
```
```bash
======================= test session starts =======================
plugins: subtests, markdown-pytest
collected 3 items

README.md::test_assert_true PASSED                           [ 33%]
README.md::test_example PASSED                               [ 66%]
README.md::test_counter SUBPASS                              [100%]
README.md::test_counter SUBPASS                              [100%]
README.md::test_counter PASSED                               [100%]
```

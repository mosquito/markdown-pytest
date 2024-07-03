import pytest
import suby


simple_code_block = """
```python
variable = 5 + 5
```
"""

simple_code_block_with_assert = """
```python
variable = 5 + 5
assert variable == 10
```
"""

simple_code_block_with_wrong_assert = """
```python
variable = 5 + 5
assert variable == 10
```
"""

simple_heading_comment = """
<!-- name: test_name -->
"""

heading_comment_with_some_code = """
<!-- name: test_name
```python
init_some_variable = 123
```
-->
"""


@pytest.mark.parametrize(
    'body',
    [
        simple_code_block,
        simple_code_block_with_assert,
    ],
)
def test_basic(body, tmp_path):
    path_to_file = tmp_path / 'test.md'
    with open(path_to_file, 'w') as file:
        file.write(simple_heading_comment + body)

    call_result = suby('pytest', '-v', str(path_to_file))

    assert call_result.returncode == 0

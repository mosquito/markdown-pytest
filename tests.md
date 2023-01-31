<!-- name: test_assert_true -->
```python
# test_assert_true
assert True
```

<!-- 
    name: test_multiline_comment_1
-->
```python
assert True
```

<!-- 
name: test_multiline_comment_2 
-->
```python
assert True
```

<!-- name: test_with_subtests -->
```python
from collections import Counter
```

<!-- 
    name: test_with_subtests; case: counter
-->
```python
counter = Counter()
```


<!-- 
    name: test_with_subtests; case: counter_add
-->
```python
counter["foo"] = 1
```


<!--- name: test_four_backticks -->
````python
# test_four_backticks
assert True
````

Split test
----------

Part one

<!--- name: test_split -->
```python
from collections import deque

queue = deque(maxlen=2)
```

Part Two

<!--- name: test_split -->
```python
queue.append(1)

assert list(queue) == [1]
```

Part Three

<!--- name: test_split -->
```python
queue.append(2)

assert list(queue) == [1, 2]
```

Part Four

<!--- name: test_split -->
`````python
queue.append(3)
assert list(queue) == [2, 3]
`````

<!--- name: test nervous backtick -->
```````````````python
# test nervous backtick
assert True
```````````````


<!--- name: test_xfail -->
```python
from pytest import xfail

xfail("it's ok")
```


<!--- name: test_raises -->
```python
from pytest import raises

with raises(AssertionError):
    assert False
```

<!-- name: test_two_dashes_name -->
```python
assert True
```

<!--- name: test_three_dashes_name --->
```python
assert True
```

<!-- name: test_mixed_dashes_name_2_3 --->
```python
assert True
```

<!--- name: test_mixed_dashes_name_3_2 -->
```python
assert True
```

<!--- name: test_blank_line_after_comment -->

```python
assert True
```

````
<!--- name: test_will_should_newer_running -->
```python
assert False
```
````


<details>
<summary>Indented code block</summary>

    <!--- name: test_overindented -->
    ```python
    assert True
    ```

</details>

# How to use conftest.py with Markdown tests

`conftest.py` is pytest's standard place for shared fixtures, hooks, and
plugins. Everything you can do in `conftest.py` for regular Python tests
works equally well for Markdown tests.

## Where to put conftest.py

pytest searches for `conftest.py` files starting from the directory of the
collected file up to the rootdir. For Markdown tests in the project root:

```{code-block} text
project/
  conftest.py      ← applies to all tests in project/
  README.md
  docs/
    conftest.py    ← applies only to docs/
    guide.md
  tests/
    conftest.py    ← applies only to tests/
    test_app.py
```

A `conftest.py` in the same directory as the Markdown file is the most
common placement.

## Defining a simple fixture

```{code-block} python
# conftest.py
import pytest

@pytest.fixture
def base_url():
    return "https://example.com"
```

Use it in Markdown:

````{code-block} markdown
<!-- name: test_url; fixtures: base_url -->
```python
assert base_url.startswith("https://")
assert "example.com" in base_url
```
````

## Fixture with setup and teardown

```{code-block} python
# conftest.py
import pytest

@pytest.fixture
def temp_database(tmp_path):
    db_path = tmp_path / "test.db"
    # setup
    db_path.write_bytes(b"")
    yield db_path
    # teardown — runs after the test
    db_path.unlink(missing_ok=True)
```

The fixture can itself use `tmp_path` — that is a built-in pytest fixture
available to all fixtures.

## Parametrised fixtures

Fixtures can be parametrised. Each parameter value creates a separate test
invocation:

```{code-block} python
# conftest.py
import pytest

@pytest.fixture(params=["sqlite", "postgres"])
def db_engine(request):
    return request.param
```

A Markdown test using `db_engine` runs twice — once with `"sqlite"` and
once with `"postgres"`.

## Session-scoped fixtures

Use `scope="session"` for expensive resources that should be created once
for the entire test run:

```{code-block} python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def compiled_schema():
    import json
    with open("schema.json") as f:
        return json.load(f)
```

Session-scoped fixtures are shared across all tests in the session,
including Markdown tests.

## autouse fixtures

An `autouse=True` fixture runs for every test without being declared in the
`fixtures:` list:

```{code-block} python
# conftest.py
import pytest

@pytest.fixture(autouse=True)
def reset_global_state():
    import mylib
    mylib.reset()
    yield
    mylib.reset()
```

All tests — Python and Markdown — receive this fixture automatically.

## Fixture factories

A factory fixture returns a callable that creates objects on demand:

```{code-block} python
# conftest.py
import pytest

@pytest.fixture
def make_user():
    created = []

    def factory(name, role="viewer"):
        user = {"name": name, "role": role}
        created.append(user)
        return user

    yield factory
    # teardown: clean up all created users
    for user in created:
        print(f"cleaning up {user['name']}")
```

Use in Markdown:

````{code-block} markdown
<!-- name: test_users; fixtures: make_user -->
```python
alice = make_user("Alice", role="admin")
bob = make_user("Bob")
assert alice["role"] == "admin"
assert bob["role"] == "viewer"
```
````

## Combining conftest fixtures with split blocks

When a test spans multiple blocks, conftest fixtures requested in the first
block are available in all subsequent blocks. You can also pull in
additional conftest fixtures in later blocks — they are merged:

````{code-block} markdown
<!-- name: test_pipeline; fixtures: make_user -->
```python
alice = make_user("Alice", role="admin")
```

<!-- name: test_pipeline; fixtures: tmp_path -->
```python
path = tmp_path / "users.json"
import json
path.write_text(json.dumps([alice]))
```

<!-- name: test_pipeline -->
```python
data = json.loads(path.read_text())
assert data[0]["name"] == "Alice"
```
````

## Debugging fixture issues

If a fixture is not found, pytest raises `FixtureLookupError` with the
fixture name and a list of available fixtures. Common causes:

- Typo in the fixture name in the `fixtures:` declaration.
- `conftest.py` is in a parent directory that pytest does not scan.
- The fixture is defined in a file that is not a `conftest.py`.

To see all available fixtures:

```{code-block} bash
pytest --fixtures guide.md
```

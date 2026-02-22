Split test with bash examples between blocks
=============================================

A single split test where non-Python fenced blocks appear between the
Python blocks. The parser must skip the bash examples and still combine
the split Python blocks into one test.

Here is how you might set up a project directory:

```bash
mkdir -p myproject/src
cd myproject
```

<!-- name: test_split_around_bash; fixtures: tmp_path -->
```python
project = tmp_path / "myproject"
project.mkdir()
src = project / "src"
src.mkdir()
```

Now create the main module:

```bash
cat > myproject/src/main.py << 'EOF'
def greet(name):
    return f"Hello, {name}!"
EOF
```

<!-- name: test_split_around_bash -->
```python
main_py = src / "main.py"
main_py.write_text('def greet(name):\n    return f"Hello, {name}!"\n')
```

And verify the project structure:

```bash
find myproject -type f
# myproject/src/main.py
```

<!-- name: test_split_around_bash -->
```python
assert main_py.exists()
assert "Hello" in main_py.read_text()
files = list(src.iterdir())
assert len(files) == 1
assert files[0].name == "main.py"
```

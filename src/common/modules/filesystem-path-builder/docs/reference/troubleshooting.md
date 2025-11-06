# Troubleshooting Guide

This guide covers common issues and their solutions when using the filesystem-path-builder module.

---

## Issue 1: AttributeError - PathTree has no attribute 'mkdir'

### Problem

```python
paths = PathTree(Path("/home/user"))
paths.config.mkdir()  # AttributeError: 'PathTree' object has no attribute 'mkdir'
```

### Cause

PathTree is for navigation only and doesn't provide filesystem operation methods like `mkdir()`.

### Solution

Convert to Path first using `to_path()`:

```python
paths = PathTree(Path("/home/user"))
paths.config.to_path().mkdir(parents=True, exist_ok=True)
```

Or use ManagedPathTree for bulk creation:

```python
managed = ManagedPathTree(
    base=Path("/home/user"),
    definitions=[PathDefinition(key="config", hidden=False)]
)
managed.create()
```

---

## Issue 2: TypeError - expected str, bytes or os.PathLike, not PathTree

### Problem

```python
paths = PathTree(Path("/home/user"))
os.listdir(paths.config)  # TypeError: expected str, bytes or os.PathLike, not PathTree
```

### Cause

PathTree doesn't implement the `os.PathLike` protocol (`__fspath__` method).

### Solution

**Option 1:** Convert to Path first:

```python
paths = PathTree(Path("/home/user"))
os.listdir(paths.config.to_path())
```

**Option 2:** Use ManagedPathTree which implements `os.PathLike`:

```python
managed = ManagedPathTree(
    base=Path("/home/user"),
    definitions=[PathDefinition(key="config", hidden=False)]
)
os.listdir(managed.config)  # Works via __fspath__
```

---

## Issue 3: FrozenInstanceError - cannot assign to field

### Problem

```python
paths = PathTree(Path("/home/user"))
paths._base = Path("/other")  # FrozenInstanceError: cannot assign to field '_base'
```

### Cause

All core classes (PathTree, ManagedPathTree, PathDefinition) are frozen dataclasses and cannot be modified after creation.

### Solution

Create a new instance instead:

```python
# Wrong
paths = PathTree(Path("/home/user"))
paths._base = Path("/other")  # Error

# Correct
paths = PathTree(Path("/other"))
```

This is by design for thread safety and immutability.

---

## Issue 4: Hidden Directory Not Created with Dot Prefix

### Problem

```python
builder = PathsBuilder(Path("/home/user"))
builder.add("config", hidden=True)
paths = builder.build()
paths.create()
# Creates /home/user/config instead of /home/user/.config
```

### Cause

The hidden flag applies to the **final segment** of the key, not intermediate segments.

### Solution

**For single-level paths:**

```python
builder = PathsBuilder(Path("/home/user"))
builder.add("config", hidden=True)  # Creates .config
paths = builder.build()
paths.create()
# Creates /home/user/.config ✓
```

**For multi-level paths:**

```python
# Only the final segment is hidden
builder = PathsBuilder(Path("/home/user"))
builder.add("dotfiles.config", hidden=True)  # Only "config" is hidden
paths = builder.build()
paths.create()
# Creates /home/user/dotfiles/.config

# To make intermediate directories hidden, define them separately
builder = PathsBuilder(Path("/home/user"))
builder.add("dotfiles", hidden=True)  # .dotfiles
builder.add("dotfiles.config", hidden=False)  # .dotfiles/config
paths = builder.build()
paths.create()
# Creates /home/user/.dotfiles/config
```

---

## Issue 5: Overlapping Path Definitions

### Problem

```python
builder = PathsBuilder(Path("/home/user"))
builder.add("config", hidden=False)
builder.add("config.app", hidden=True)
paths = builder.build()
paths.create()
# What happens to "config"?
```

### Cause

When paths overlap, the first definition wins. The second definition extends the first.

### Solution

This is expected behavior. The module creates:
- `/home/user/config` (from first definition)
- `/home/user/config/.app` (from second definition, only "app" is hidden)

If you want both to be hidden:

```python
builder = PathsBuilder(Path("/home/user"))
builder.add("config", hidden=True)  # .config
builder.add("config.app", hidden=False)  # .config/app
paths = builder.build()
```

---

## Issue 6: AttributeError with Underscore-Prefixed Names

### Problem

```python
paths = PathTree(Path("/home/user"))
private = paths._private  # AttributeError
```

### Cause

PathTree reserves names starting with underscore for internal use and raises AttributeError for such names.

### Solution

Use bracket notation instead:

```python
paths = PathTree(Path("/home/user"))
private = paths["_private"]  # Works
```

Or use slash operator:

```python
paths = PathTree(Path("/home/user"))
private = paths / "_private"  # Works
```

---

## Issue 7: Path Not Expanded (Environment Variables)

### Problem

```python
paths = PathTree(Path("$HOME/myapp"))
print(paths.to_path())  # Prints: $HOME/myapp (not expanded)
```

### Cause

Path expansion happens during PathTree/PathsBuilder initialization, but only if you use the correct method.

### Solution

Use `expanduser()` and `resolve()`:

```python
# Wrong
paths = PathTree(Path("$HOME/myapp"))

# Correct
paths = PathTree(Path("$HOME/myapp").expanduser().resolve())

# Or use PathsBuilder which does this automatically
builder = PathsBuilder(Path("$HOME/myapp"))  # Automatically expands
paths = builder.build()
```

PathsBuilder automatically expands paths in its `__init__`:

```python
def __init__(self, base: Segment) -> None:
    self._base = Path(base).expanduser().resolve()
```

---

## Issue 8: Type Checker Errors with Navigation

### Problem

```python
paths = PathTree(Path("/home/user"))
config: Path = paths.config  # Type error: expected Path, got PathTree
```

### Cause

Navigation returns PathTree, not Path. Type checkers correctly identify this.

### Solution

Convert to Path explicitly:

```python
paths = PathTree(Path("/home/user"))
config: Path = paths.config.to_path()  # Correct type
```

Or use PathTree type:

```python
paths = PathTree(Path("/home/user"))
config: PathTree = paths.config  # Correct type
config_path: Path = config.to_path()  # Convert when needed
```

---

## Common Questions

### Q1: Why doesn't PathTree implement os.PathLike?

**A:** PathTree is designed for navigation only, not as a path object. It's a lightweight wrapper that creates Path objects on-demand. ManagedPathTree implements os.PathLike because it represents a concrete path with a registry.

**Solution:** Use `to_path()` to convert, or use ManagedPathTree.

---

### Q2: Can I modify a PathTree after creation?

**A:** No, all core classes are frozen dataclasses for thread safety and immutability.

**Solution:** Create a new instance with the desired configuration.

---

### Q3: How do I create nested hidden directories?

**A:** Define each level separately with its own hidden flag.

```python
builder = PathsBuilder(Path.home())
builder.add("dotfiles", hidden=True)  # .dotfiles
builder.add("dotfiles.config", hidden=False)  # .dotfiles/config
builder.add("dotfiles.config.app", hidden=True)  # .dotfiles/config/.app
paths = builder.build()
paths.create()
```

---

### Q4: Why do I get "first definition wins" behavior?

**A:** This is by design. The module doesn't merge overlapping definitions. The first definition creates the path, and subsequent definitions extend it.

**Solution:** Define paths in the order you want them created, with appropriate hidden flags.

---

### Q5: Can I use PathTree with async code?

**A:** Yes, PathTree is thread-safe and can be used in async code. However, filesystem operations (like `create()`) are synchronous.

```python
import asyncio
from pathlib import Path
from filesystem_path_builder import PathTree

async def process_file(paths: PathTree, filename: str):
    file_path = paths.data / filename
    # Use asyncio file operations
    async with aiofiles.open(file_path.to_path(), 'r') as f:
        content = await f.read()
    return content
```

---

### Q6: How do I handle Windows paths?

**A:** The module uses pathlib.Path which handles platform differences automatically.

```python
# Works on both Unix and Windows
paths = PathTree(Path.home() / "myapp")
config = paths.config.to_path()
# Unix: /home/user/myapp/config
# Windows: C:\Users\user\myapp\config
```

---

### Q7: Can I use relative paths?

**A:** Yes, but it's recommended to resolve them first.

```python
# Relative path (not recommended)
paths = PathTree(Path("./myapp"))

# Absolute path (recommended)
paths = PathTree(Path("./myapp").resolve())

# Or use PathsBuilder which resolves automatically
builder = PathsBuilder(Path("./myapp"))  # Automatically resolves
```

---

### Q8: How do I debug path building?

**A:** Use `repr()` to see the internal structure:

```python
paths = PathTree(Path("/home/user"))
config = paths.config.app

print(repr(config))
# PathTree(base=PosixPath('/home/user'), segments=('config', 'app'))

print(str(config))
# /home/user/config/app

print(config.to_path())
# /home/user/config/app
```

For ManagedPathTree, inspect the definitions:

```python
managed = ManagedPathTree(
    base=Path("/home/user"),
    definitions=[PathDefinition(key="config.app", hidden=True)]
)

print(managed._definitions)
# (PathDefinition(key='config.app', hidden=True),)
```

---

## Performance Issues

### Issue: Slow Path Building

**Problem:** Creating many PathTree instances is slow.

**Solution:** Reuse PathTree instances:

```python
# Slow
for i in range(1000):
    paths = PathTree(Path("/home/user"))
    config = paths.config.to_path()

# Fast
paths = PathTree(Path("/home/user"))
config = paths.config.to_path()
for i in range(1000):
    # Use config
    pass
```

---

### Issue: High Memory Usage

**Problem:** Many PathTree instances consume too much memory.

**Solution:** PathTree uses `__slots__` for memory efficiency, but if you're creating millions of instances, consider using Path directly:

```python
# If you need millions of paths, use Path directly
base = Path("/home/user")
paths = [base / f"file_{i}.txt" for i in range(1000000)]

# PathTree is best for structured navigation, not mass path generation
```

---

## Development Issues

### Issue: Module Changes Not Reflected After `uv sync`

**Problem:**

You make changes to the filesystem-path-builder source code, but when you run your application, the changes aren't reflected. Running `uv sync` seems to overwrite your changes.

```python
# You added a new parameter to PathsBuilder
builder = PathsBuilder(Path("/home/user"), strict=True)
# TypeError: __init__() got an unexpected keyword argument 'strict'
```

**Cause:**

The module is installed in **non-editable mode** instead of editable mode. This means the package files are copied to `site-packages` instead of being symlinked to the source directory.

**Diagnosis:**

Check if the module is installed in editable mode:

```bash
cat .venv/lib/python3.12/site-packages/filesystem_path_builder-*.dist-info/direct_url.json
```

If you see `"editable":false`, the module is not in editable mode.

**Solution:**

**Option 1: Fix `pyproject.toml` (Recommended)**

Add `editable = true` to the `[tool.uv.sources]` section:

```toml
[tool.uv.sources]
filesystem-path-builder = { path = "../../common/modules/filesystem-path-builder", editable = true }
```

Then run:
```bash
uv lock
uv sync
```

**Option 2: Manual Reinstall**

```bash
# Uninstall the package
uv pip uninstall filesystem-path-builder

# Reinstall in editable mode
uv pip install -e ../../common/modules/filesystem-path-builder --no-deps

# Update lockfile
uv lock
```

**Prevention:**

Always use `editable = true` in `[tool.uv.sources]` for local path dependencies that you're actively developing.

---

### Issue: `--force-reinstall` Creates Non-Editable Install

**Problem:**

Using `uv pip install -e ... --force-reinstall` creates a non-editable install instead of an editable one.

**Cause:**

The `--force-reinstall` flag in `uv` causes the package to be copied instead of symlinked, even with the `-e` flag.

**Solution:**

Uninstall first, then install without `--force-reinstall`:

```bash
# Wrong - creates non-editable install
uv pip install -e . --force-reinstall --no-deps

# Correct - creates editable install
uv pip uninstall -y filesystem-path-builder
uv pip install -e . --no-deps
```

**Verification:**

Check that the install is editable:

```bash
cat .venv/lib/python3.12/site-packages/filesystem_path_builder-*.dist-info/direct_url.json
# Should show: "editable":true
```

---

### Issue: Changes to Source Code Not Reflected

**Problem:**

You edit the source code but the changes don't appear when you import the module.

**Possible Causes:**

1. **Non-editable install** - See "Module Changes Not Reflected" above
2. **Python bytecode cache** - Old `.pyc` files are being used
3. **Module already imported** - Python caches imported modules

**Solutions:**

**For bytecode cache:**
```bash
# Clean all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} +

# Or use Python's built-in
python -Bc "import compileall; compileall.compile_dir('.', force=True)"
```

**For cached imports (in Python REPL or Jupyter):**
```python
# Reload the module
import importlib
import filesystem_path_builder
importlib.reload(filesystem_path_builder)
```

**For persistent issues:**
```bash
# Complete cleanup
uv pip uninstall filesystem-path-builder
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
uv pip install -e . --no-deps
```

---

## Getting Help

If you encounter an issue not covered here:

1. Check the [API Reference](../api/pathtree.md)
2. Review [Usage Patterns](../guides/usage_patterns.md)
3. Check the [Investigation Notes](../helpers/INVESTIGATION_NOTES.md) for detailed implementation details
4. File an issue on the project repository

---

**Related Documentation:**
- [Getting Started](../guides/getting_started.md)
- [Usage Patterns](../guides/usage_patterns.md)
- [API Reference](../api/pathtree.md)

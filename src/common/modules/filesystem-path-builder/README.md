# Filesystem Path Builder

**Version:** 0.1.0
**Python:** >=3.12
**Dependencies:** None (stdlib only)

---

## Overview

A scalable filesystem path navigation and builder module with support for hidden directories. Provides two complementary approaches:

1. **PathTree**: Dynamic, attribute-based directory navigation
2. **PathsBuilder**: Explicit path definition with hidden directory support

---

## Features

- ✅ **Zero Dependencies** - Uses only Python stdlib (pathlib, dataclasses, typing)
- ✅ **Immutable** - Frozen dataclasses prevent accidental modifications
- ✅ **Type-Safe** - Full type hints for IDE support
- ✅ **Hidden Directories** - Support for Unix-style hidden directories (dot-prefixed)
- ✅ **Flexible Navigation** - Attribute access, bracket notation, or `/` operator
- ✅ **Explicit File Access** - Clear separation between directories and files
- ✅ **Environment Variables** - Automatic expansion of `$HOME`, `~`, etc.

---

## Installation

```bash
cd src/common/modules/filesystem-path-builder
uv pip install -e .
```

---

## Quick Start

### PathTree - Dynamic Navigation

```python
from filesystem_path_builder import PathTree

# Create from base directory
paths = PathTree.from_str("~/dotfiles")

# Navigate using attributes
config = paths.config.nvim
print(config.path)  # PosixPath('/home/user/dotfiles/config/nvim')

# Access files explicitly
init_lua = config.file("init.lua")
print(init_lua)  # PosixPath('/home/user/dotfiles/config/nvim/init.lua')

# Create directories
config.ensure_dir()

# Check existence
if config.exists_dir():
    print("Config exists!")
```

### PathsBuilder - Explicit Configuration

```python
from filesystem_path_builder import PathsBuilder
from pathlib import Path

# Define paths explicitly (use underscores for attribute access)
builder = PathsBuilder(Path.home() / "dotfiles")
builder.add_path("dotfiles", hidden=True)
builder.add_path("dotfiles.starship", hidden=True)
builder.add_path("dotfiles.zsh", hidden=True)
builder.add_path("config", hidden=True)
builder.add_path("scripts", hidden=False)

# Build namespace
paths = builder.build()

# Use paths individually (attribute access)
paths.dotfiles.ensure_dir()   # Creates ~/.dotfiles
paths.scripts.ensure_dir()    # Creates ~/dotfiles/scripts

# Or create all directories at once
builder.create()  # Creates all defined directories

# Note: Keys are stored exactly as registered
# For attribute access, use Python-friendly names (lowercase, underscores)
# For paths with hyphens or spaces, use bracket notation:
builder.add_path("my-config")  # Register with hyphen
paths["my-config"].path        # Access with bracket notation
```

---

## Documentation

- **[API Reference](docs/API.md)** - Complete API documentation for all classes and methods
- **[Usage Guide](docs/USAGE.md)** - Common patterns, best practices, and examples

---

## Use Cases

### 1. Dotfiles Installer

```python
from filesystem_path_builder import PathsBuilder
from pathlib import Path

builder = PathsBuilder(Path.home() / ".config")
builder.add_path("nvim", hidden=False)
builder.add_path("nvim.lua", hidden=False)
builder.add_path("nvim.lua.plugins", hidden=False)
builder.add_path("starship", hidden=False)

paths = builder.build()
paths.nvim.lua.plugins.ensure_dir()

# For paths with hyphens, use underscores in registration for attribute access
builder.add_path("oh_my_zsh", hidden=True)  # Use underscores
paths.oh_my_zsh.ensure_dir()                # Access with underscores

# Or use hyphens with bracket notation
builder.add_path("oh-my-zsh", hidden=True)  # Use hyphens
paths["oh-my-zsh"].ensure_dir()             # Access with brackets
```

### 2. Project Structure Management

```python
from filesystem_path_builder import PathTree

project = PathTree.from_str("~/projects/myapp")

# Create standard structure
project.src.ensure_dir()
project.tests.ensure_dir()
project.docs.ensure_dir()

# Access files
readme = project.file("README.md")
config = project.src.file("config.py")
```

### 3. Dynamic Path Building

```python
from filesystem_path_builder import PathTree

base = PathTree.from_str("/tmp/data")

# Dynamic navigation
for module in ["auth", "api", "db"]:
    module_path = base[module]
    module_path.ensure_dir()
    module_path.file("__init__.py").touch()
```

---

## API Reference

See `docs/api/` for detailed API documentation.

---

## Documentation

Complete documentation is available in the `docs/` directory:

- **Architecture**: `docs/architecture/`
- **API Reference**: `docs/api/`
- **Usage Guides**: `docs/guides/`
- **Examples**: `docs/reference/`

---

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/

# Format code
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/
```

---

## License

MIT

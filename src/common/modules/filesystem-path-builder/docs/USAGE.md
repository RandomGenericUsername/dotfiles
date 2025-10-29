# Usage Guide

## Installation

The module is installed as a local dependency:

```bash
# In your project's pyproject.toml
[tool.uv.sources]
filesystem-path-builder = { path = "path/to/filesystem-path-builder" }
```

## Basic Usage

### PathTree - Dynamic Navigation

Use PathTree for simple, dynamic directory navigation:

```python
from filesystem_path_builder import PathTree

# Create from base directory
paths = PathTree.from_str("~/dotfiles")

# Navigate using attributes
config = paths.config.nvim
print(config.path)  # /home/user/dotfiles/config/nvim

# Create directories
config.ensure_dir()

# Access files
init_lua = config.file("init.lua")
print(init_lua)  # /home/user/dotfiles/config/nvim/init.lua

# Check existence
if config.exists_dir():
    print("Config exists!")
```

### PathsBuilder - Explicit Configuration

Use PathsBuilder when you need explicit control over hidden directories:

```python
from filesystem_path_builder import PathsBuilder
from pathlib import Path

# Define paths explicitly
builder = PathsBuilder(Path.home() / "dotfiles")
builder.add_path("dotfiles", hidden=True)
builder.add_path("dotfiles.starship", hidden=True)
builder.add_path("dotfiles.zsh", hidden=True)
builder.add_path("config", hidden=True)
builder.add_path("scripts", hidden=False)

# Build namespace
paths = builder.build()

# Use paths individually
paths.dotfiles.ensure_dir()   # Creates ~/.dotfiles
paths.scripts.ensure_dir()    # Creates ~/dotfiles/scripts

# Or create all at once
builder.create()  # Creates all defined directories
```

## Common Patterns

### Pattern 1: Dotfiles Installer (Recommended)

```python
from filesystem_path_builder import PathsBuilder
from pathlib import Path

# Define dotfiles structure
builder = PathsBuilder(Path.home())
builder.add_path("dotfiles", hidden=True)
builder.add_path("dotfiles.config", hidden=True)
builder.add_path("dotfiles.config.nvim", hidden=False)
builder.add_path("dotfiles.config.starship", hidden=False)

# Build returns ManagedPathTree with create() and navigation
paths = builder.build()

# Create all directories at once
paths.create()

# Navigate to specific paths
nvim_config = paths.dotfiles.config.nvim.file("init.lua")
starship_config = paths.dotfiles.config.starship.file("starship.toml")

# Get root path
install_root = paths.path  # or str(paths) via __fspath__
```

### Pattern 2: Project Structure Management

```python
from filesystem_path_builder import PathTree

# Define project structure
project = PathTree.from_str("~/projects/myapp")

# Create directory structure
project.src.ensure_dir()
project.tests.ensure_dir()
project.docs.ensure_dir()

# Create files
project.src.ensure_file("__init__.py")
project.tests.ensure_file("test_main.py")
```

### Pattern 3: Configuration Paths

```python
from filesystem_path_builder import PathTree

# XDG-style config paths
config = PathTree.from_str("$XDG_CONFIG_HOME")

# Access application configs
nvim = config.nvim
starship = config.starship
zsh = config.zsh

# Create config files
nvim.ensure_file("init.lua")
starship.ensure_file("starship.toml")
```

### Pattern 4: Dynamic Path Building

```python
from filesystem_path_builder import PathTree

base = PathTree.from_str("~/projects")

# Dynamic navigation
for module in ["auth", "api", "db"]:
    module_path = base[module]
    module_path.ensure_dir()
    module_path.file("__init__.py").touch()
```

### Pattern 5: Checking Existence Before Operations

```python
from filesystem_path_builder import PathTree

paths = PathTree.from_str("~/dotfiles")

# Check before creating
if not paths.config.exists_dir():
    paths.config.ensure_dir()

# Check file existence
if paths.config.exists_file("settings.toml"):
    # Load settings
    pass
else:
    # Create default settings
    paths.config.ensure_file("settings.toml")
```

## Navigation Methods

### Attribute Access

Best for simple, known directory names:

```python
paths.config.nvim.lua.plugins
```

### Bracket Notation

Use for special characters or dynamic names:

```python
paths["my-config"]  # Hyphens
paths[variable]     # Dynamic
```

### Slash Operator

Use for path-like construction:

```python
paths / "config" / "nvim"
```

### Mixed Navigation

Combine methods as needed:

```python
paths.config["nvim-custom"] / "lua"
```

## Hidden Directories

Hidden directories are created with a dot prefix:

```python
# Using PathTree
hidden = PathTree.from_str("/tmp/test", hidden=True)
hidden.ensure_dir()  # Creates /tmp/.test

# Using PathsBuilder
builder = PathsBuilder(Path("/tmp"))
builder.add_path("config", hidden=True)
builder.create()  # Creates /tmp/.config
```

## Environment Variables

PathTree automatically expands environment variables:

```python
# Tilde expansion
paths = PathTree.from_str("~/dotfiles")

# Environment variables
paths = PathTree.from_str("$HOME/.config")
paths = PathTree.from_str("$XDG_CONFIG_HOME/nvim")
```

## Best Practices

### 1. Use Explicit File Access

Always use `.file()` for files to make code clear:

```python
# Good
config_file = paths.config.file("settings.toml")

# Avoid
config_file = paths.config.settings_toml  # Unclear if file or dir
```

### 2. Check Existence Before Operations

```python
if not paths.config.exists_dir():
    paths.config.ensure_dir()
```

### 3. Use PathsBuilder for Complex Structures

When you have many paths with different hidden status:

```python
builder = PathsBuilder(root)
builder.add_path("a", hidden=True)
builder.add_path("b", hidden=False)
# ... many more paths
builder.create()  # Create all at once
```

### 4. Store Base in Configuration

```python
# In config
BASE_DIR = Path.home() / "dotfiles"

# In code
paths = PathTree.from_str(BASE_DIR)
```

### 5. Use Environment Variables for Portability

```python
# Works across different systems
paths = PathTree.from_str("$HOME/.config")
```

## Error Handling

```python
from pathlib import Path
from filesystem_path_builder import PathTree

paths = PathTree.from_str("/tmp/test")

try:
    paths.config.ensure_dir()
except PermissionError:
    print("No permission to create directory")
except OSError as e:
    print(f"OS error: {e}")
```

## Thread Safety

PathTree is immutable (frozen dataclass), making it thread-safe for reading:

```python
# Safe to share across threads
paths = PathTree.from_str("~/dotfiles")

# Each navigation creates a new instance
config1 = paths.config  # Thread 1
config2 = paths.config  # Thread 2
# config1 and config2 are separate instances
```

## Performance Tips

1. **Reuse PathTree instances**: They're immutable and can be safely reused
2. **Use `ensure_dir()` instead of checking + creating**: It's atomic
3. **Use `builder.create()` for bulk operations**: More efficient than individual calls


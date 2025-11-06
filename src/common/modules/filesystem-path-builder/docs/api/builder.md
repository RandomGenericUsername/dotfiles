# PathsBuilder API Reference

## Overview

`PathsBuilder` is a builder pattern class for explicitly defining directory structures with support for hidden directories, key sanitization, and strict mode validation. It provides a fluent interface for configuring paths before building a `ManagedPathTree` instance.

**Module:** `filesystem_path_builder.builder`
**Type:** Regular class (not frozen)
**Related Classes:** `ManagedPathTree`, `PathDefinition`

---

## Class Definition

```python
class PathsBuilder:
    """Builder for explicitly defining directory structures."""
    
    def __init__(self, root: Path, strict: bool = False):
        self.root = Path(root)
        self.strict = strict
        self.definitions: dict[str, PathDefinition] = {}
```

---

## Constructor

### `__init__(root: Path, strict: bool = False)`

Create a new PathsBuilder instance.

**Parameters:**
- `root` (Path): Root directory for all paths
- `strict` (bool): If True, only registered paths can be accessed. If False (default), allows dynamic navigation beyond registered paths.

**Returns:** PathsBuilder instance

**Example:**

```python
from pathlib import Path
from filesystem_path_builder import PathsBuilder

# Flexible mode (default) - allows dynamic navigation
builder = PathsBuilder(Path.home() / "dotfiles")

# Strict mode - only registered paths allowed
builder = PathsBuilder(Path.home() / "dotfiles", strict=True)
```

---

## Methods

### `add_path(key: str, hidden: bool = False) -> PathsBuilder`

Add a path definition to the builder.

**Parameters:**
- `key` (str): Dot-separated path key (e.g., "dotfiles.Oh-My Zsh")
- `hidden` (bool): Whether this directory should be hidden (prefixed with `.`)

**Returns:** Self for method chaining

**Key Sanitization:**

The key is automatically sanitized for Python attribute access:
- Converted to lowercase
- Spaces replaced with underscores
- Hyphens replaced with underscores
- Dots preserved (for nesting)

The original key is preserved for directory creation, allowing natural names with mixed case, spaces, and hyphens.

**Example:**

```python
builder = PathsBuilder(Path.home() / "dotfiles")

# Simple paths
builder.add_path("config", hidden=True)  # Creates .config

# Nested paths
builder.add_path("dotfiles.starship", hidden=True)  # Creates .dotfiles/.starship

# Mixed case, spaces, hyphens (sanitized for access)
builder.add_path("dotfiles.Oh-My Zsh", hidden=True)
# Access: paths.dotfiles.oh_my_zsh
# Creates: .dotfiles/.Oh-My Zsh

builder.add_path("Wallpapers Directory", hidden=False)
# Access: paths.wallpapers_directory
# Creates: Wallpapers Directory

# Method chaining
builder.add_path("config", hidden=True) \
       .add_path("config.nvim", hidden=False) \
       .add_path("config.starship", hidden=False)
```

**Notes:**
- The hidden flag applies to the **final segment** of the key
- For nested paths, define each level separately to control hidden status
- Keys are normalized for registry lookups but original names preserved for directory creation

---

### `build() -> ManagedPathTree`

Build a ManagedPathTree with all definitions.

**Returns:** ManagedPathTree instance with full registry

**Example:**

```python
builder = PathsBuilder(Path.home() / "dotfiles")
builder.add_path("dotfiles", hidden=True)
builder.add_path("scripts", hidden=False)

# Build the tree
paths = builder.build()

# Now you can navigate and create
paths.create()  # Create all directories
config_path = paths.dotfiles.path  # Navigate to paths
```

**Notes:**
- Returns a `ManagedPathTree` which combines navigation and creation
- The registry is copied, so further changes to the builder don't affect the tree
- Strict mode setting is passed to the ManagedPathTree

---

### `create() -> list[Path]`

Create all defined directories on the filesystem.

**Returns:** List of Path objects for all created directories

**Example:**

```python
builder = PathsBuilder(Path.home() / ".config")
builder.add_path("nvim", hidden=False)
builder.add_path("nvim.lua", hidden=False)
builder.add_path("nvim.lua.plugins", hidden=False)
builder.add_path("starship", hidden=False)

# Create all directories
created = builder.create()

# All directories are now created on disk
for path in created:
    print(f"Created: {path}")
```

**Notes:**
- Creates directories with `parents=True, exist_ok=True`
- Respects hidden flag for each directory level
- Returns list of all created paths

---

## Strict Mode

Strict mode enforces that only registered paths can be accessed, helping catch typos and ensuring all paths are explicitly defined.

### Flexible Mode (Default)

```python
builder = PathsBuilder(Path.home() / "dotfiles")
builder.add_path("config", hidden=True)
paths = builder.build()

# Registered path - works
config = paths.config.path  # OK

# Unregistered path - also works (dynamic navigation)
scripts = paths.scripts.path  # OK - creates path dynamically
```

### Strict Mode

```python
builder = PathsBuilder(Path.home() / "dotfiles", strict=True)
builder.add_path("config", hidden=True)
paths = builder.build()

# Registered path - works
config = paths.config.path  # OK

# Unregistered path - raises AttributeError
scripts = paths.scripts.path  # AttributeError: Path 'scripts' is not registered
```

**When to Use Strict Mode:**
- ✅ Production code where all paths should be explicitly defined
- ✅ Configuration files where typos could cause issues
- ✅ Large projects where you want to catch path access errors early
- ❌ Exploratory code or scripts
- ❌ When you need dynamic path navigation

---

## Key Sanitization

The `_sanitize_key()` function normalizes path keys for Python attribute access while preserving original names for directory creation.

### Sanitization Rules

1. **Lowercase:** All characters converted to lowercase
2. **Spaces → Underscores:** Spaces replaced with underscores
3. **Hyphens → Underscores:** Hyphens replaced with underscores
4. **Dots Preserved:** Dots kept for nesting

### Examples

| Original Key | Sanitized Key | Access | Directory Created |
|--------------|---------------|--------|-------------------|
| `"dotfiles"` | `"dotfiles"` | `paths.dotfiles` | `dotfiles` |
| `"Oh-My-Zsh"` | `"oh_my_zsh"` | `paths.oh_my_zsh` | `Oh-My-Zsh` |
| `"Wallpapers Directory"` | `"wallpapers_directory"` | `paths.wallpapers_directory` | `Wallpapers Directory` |
| `"dotfiles.Oh-My Zsh"` | `"dotfiles.oh_my_zsh"` | `paths.dotfiles.oh_my_zsh` | `dotfiles/Oh-My Zsh` |

---

## Usage Patterns

### Pattern 1: Simple Configuration

```python
builder = PathsBuilder(Path.home() / ".config")
builder.add_path("nvim", hidden=False)
builder.add_path("starship", hidden=False)
builder.add_path("zsh", hidden=False)

paths = builder.build()
paths.create()
```

### Pattern 2: Nested Structure

```python
builder = PathsBuilder(Path.home() / "dotfiles")
builder.add_path("dotfiles", hidden=True)
builder.add_path("dotfiles.config", hidden=False)
builder.add_path("dotfiles.config.nvim", hidden=False)
builder.add_path("dotfiles.scripts", hidden=False)

paths = builder.build()
paths.create()
```

### Pattern 3: Method Chaining

```python
paths = (PathsBuilder(Path.home() / ".config")
    .add_path("nvim", hidden=False)
    .add_path("nvim.lua", hidden=False)
    .add_path("starship", hidden=False)
    .build())

paths.create()
```

### Pattern 4: Strict Mode for Production

```python
# Define all paths explicitly
builder = PathsBuilder(Path("/var/app"), strict=True)
builder.add_path("config", hidden=False)
builder.add_path("data", hidden=False)
builder.add_path("logs", hidden=False)
builder.add_path("temp", hidden=False)

paths = builder.build()

# Only registered paths work
config = paths.config.path  # OK
data = paths.data.path  # OK
cache = paths.cache.path  # AttributeError - not registered
```

---

## See Also

- [ManagedPathTree API](managed_pathtree.md) - Extended PathTree with creation
- [PathDefinition API](path_definition.md) - Path configuration dataclass
- [Usage Patterns](../guides/usage_patterns.md) - Common usage patterns
- [Troubleshooting](../reference/troubleshooting.md) - Common issues

---

**Next:** [ManagedPathTree API](managed_pathtree.md) | [PathDefinition API](path_definition.md)


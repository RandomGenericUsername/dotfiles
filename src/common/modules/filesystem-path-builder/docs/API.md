# API Reference

## PathTree

Immutable, attribute-based directory navigation.

### Constructor

```python
PathTree(base: Path, rel: Path = Path(), hidden: bool = False)
```

**Parameters:**
- `base`: Root directory
- `rel`: Relative path from base (default: empty)
- `hidden`: Whether directory should be hidden with dot prefix (default: False)

### Class Methods

#### `from_str(base: str | Path, hidden: bool = False) -> PathTree`

Create PathTree from string path, expanding environment variables.

```python
paths = PathTree.from_str("~/dotfiles")
paths = PathTree.from_str("$HOME/.config")
```

### Properties

#### `path: Path`

Get the full resolved path (base + rel).

```python
paths = PathTree.from_str("/tmp")
print(paths.config.nvim.path)  # /tmp/config/nvim
```

### Navigation Methods

#### `__getattr__(name: str) -> PathTree`

Navigate via attribute access.

```python
paths.config.nvim  # Navigate to config/nvim
paths.class_       # Trailing underscore for Python keywords
```

#### `__getitem__(key: str | Path) -> PathTree`

Navigate via bracket notation (for special characters or dynamic names).

```python
paths["foo-bar"]   # Hyphens not allowed in attributes
paths[var_name]    # Dynamic navigation
```

#### `__truediv__(segment: str | Path) -> PathTree`

Navigate via `/` operator.

```python
paths / "config" / "nvim"
```

#### `up(levels: int = 1) -> PathTree`

Navigate up the directory tree.

```python
deep = paths.a.b.c.d
deep.up(2)  # Navigate to a.b
```

### File Methods

#### `file(filename: str | Path) -> Path`

Get path to a file in this directory.

```python
paths.config.file("settings.toml")  # /path/config/settings.toml
```

#### `ensure_file(filename: str | Path, touch_exists_ok: bool = True) -> Path`

Create file and parent directories.

```python
paths.config.ensure_file("settings.toml")
```

#### `exists_file(filename: str | Path) -> bool`

Check if file exists.

```python
if paths.config.exists_file("settings.toml"):
    print("Settings exist")
```

### Directory Methods

#### `ensure_dir() -> Path`

Create directory (and parents) if it doesn't exist. Applies hidden flag.

```python
paths.config.nvim.ensure_dir()  # Creates /path/config/nvim
```

#### `exists_dir() -> bool`

Check if directory exists.

```python
if paths.config.exists_dir():
    print("Config directory exists")
```

#### `is_dir() -> bool`

Check if path exists and is a directory.

```python
if paths.config.is_dir():
    print("Is a directory")
```

#### `exists() -> bool`

Check if path exists (file or directory).

```python
if paths.config.exists():
    print("Path exists")
```

#### `is_file() -> bool`

Check if path exists and is a file.

```python
if paths.readme.is_file():
    print("Is a file")
```

### Utility Methods

#### `resolve() -> Path`

Resolve to absolute path.

```python
paths.config.resolve()  # Absolute path
```

---

## PathsBuilder

Builder pattern for explicit path definition with hidden status.

### Constructor

```python
PathsBuilder(root: Path)
```

**Parameters:**
- `root`: Root directory for all paths

### Methods

#### `add_path(key: str, hidden: bool = False) -> PathsBuilder`

Add a path definition. Returns self for chaining.

**Parameters:**
- `key`: Dot-separated path (e.g., "config.nvim")
- `hidden`: Whether directory should be hidden

```python
builder = PathsBuilder(Path.home() / "dotfiles")
builder.add_path("config", hidden=True)
builder.add_path("config.nvim", hidden=False)
builder.add_path("scripts", hidden=False)
```

#### `build() -> ManagedPathTree`

Build a ManagedPathTree with all defined paths and create() capability.

```python
paths = builder.build()
paths.create()         # Create all directories
paths.config.path      # Navigate to paths
paths.config.nvim.path
```

#### `create() -> list[Path]`

Create all defined directories on filesystem. Returns list of created paths.

```python
created = builder.create()  # Creates all directories
```

---

## ManagedPathTree

PathTree with registry and create() capability. Extends PathTree with directory creation.

### Constructor

```python
ManagedPathTree(
    base: Path,
    rel: Path = Path(),
    hidden: bool = False,
    _registry: dict[str, PathDefinition] = {}
)
```

**Parameters:**
- `base`: Root directory
- `rel`: Relative path from base (default: empty)
- `hidden`: Whether directory should be hidden (default: False)
- `_registry`: Internal registry of path definitions (default: empty dict)

**Note:** Typically created via `PathsBuilder.build()`, not directly.

### Methods

All PathTree methods are available, plus:

#### `create() -> list[Path]`

Create all registered directories on the filesystem.

```python
paths = builder.build()
created = paths.create()  # Creates all registered directories
```

#### `__fspath__() -> str`

Support os.PathLike protocol for use with os functions.

```python
import os
paths = builder.build()
os.chdir(paths.config)  # Works because of __fspath__
```

### Navigation

All navigation methods return ManagedPathTree instead of PathTree, preserving the registry:

```python
paths = builder.build()
config = paths.config           # Returns ManagedPathTree
nvim = paths.config.nvim        # Returns ManagedPathTree
lua = paths / "config" / "lua"  # Returns ManagedPathTree
```

---

## PathDefinition

Dataclass holding path definition.

### Attributes

- `key: str` - Dot-separated path key
- `hidden: bool` - Whether directory is hidden (default: False)

### Methods

#### `get_parts() -> list[str]`

Split key into path components.

```python
pd = PathDefinition(key="config.nvim", hidden=False)
pd.get_parts()  # ["config", "nvim"]
```

---

## Type Aliases

### Segment

```python
Segment = Union[str, Path]
```

Used for path navigation methods that accept either strings or Path objects.


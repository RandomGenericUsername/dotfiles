# PathTree API Reference

## Overview

`PathTree` is an immutable, frozen dataclass that provides dynamic, attribute-based navigation through directory structures without performing filesystem I/O during navigation.

**Module:** `filesystem_path_builder.pathtree`
**Type:** Frozen dataclass with slots
**Inheritance:** None (base class)

---

## Class Definition

```python
@dataclass(frozen=True, slots=True)
class PathTree:
    """Immutable path navigation with dynamic attribute access."""
    _base: Path
    _segments: tuple[str, ...] = field(default_factory=tuple)
```

---

## Constructor

### `__init__(base: Segment, segments: tuple[str, ...] = ())`

Create a new PathTree instance.

**Parameters:**
- `base` (Segment): Base directory path (str or Path)
- `segments` (tuple[str, ...]): Path segments for navigation (default: empty tuple)

**Returns:** PathTree instance

**Example:**

```python
from pathlib import Path
from filesystem_path_builder import PathTree

# From string
paths = PathTree("/home/user")

# From Path
paths = PathTree(Path("/home/user"))

# With segments (usually not used directly)
paths = PathTree(Path("/home/user"), segments=("config", "app"))
```

---

## Navigation Methods

### `__getattr__(name: str) -> PathTree`

Navigate to a subdirectory using attribute access.

**Parameters:**
- `name` (str): Directory name

**Returns:** New PathTree with additional segment

**Raises:**
- `AttributeError`: If name starts with underscore (reserved)

**Example:**

```python
paths = PathTree(Path("/home/user"))

# Navigate using attributes
config = paths.config  # PathTree with segments=("config",)
app = paths.config.app  # PathTree with segments=("config", "app")

# Convert to Path
path = app.to_path()  # Path("/home/user/config/app")
```

**Notes:**
- Does not perform filesystem I/O
- Returns new PathTree (immutable)
- Names starting with `_` raise AttributeError

---

### `__getitem__(key: str) -> PathTree`

Navigate to a subdirectory using bracket notation.

**Parameters:**
- `key` (str): Directory name

**Returns:** New PathTree with additional segment

**Example:**

```python
paths = PathTree(Path("/home/user"))

# Navigate using brackets
config = paths["config"]
app = paths["config"]["app"]

# Useful for dynamic names
dir_name = "config"
config = paths[dir_name]

# Useful for names with special characters
special = paths["my-config"]  # Can't use attribute access
```

**Notes:**
- Equivalent to `__getattr__` but works with any string
- Useful for dynamic directory names
- Useful for names that aren't valid Python identifiers

---

### `__truediv__(other: Segment) -> PathTree`

Navigate using the `/` operator.

**Parameters:**
- `other` (Segment): Directory name (str or Path)

**Returns:** New PathTree with additional segment(s)

**Example:**

```python
paths = PathTree(Path("/home/user"))

# Navigate using /
config = paths / "config"
app = paths / "config" / "app"

# Mix with attribute access
mixed = paths.config / "app"

# Use with Path
from pathlib import Path
app = paths / Path("config/app")
```

**Notes:**
- Most flexible navigation method
- Works with str and Path
- Can include multiple segments in one operation

---

## Conversion Methods

### `to_path() -> Path`

Convert PathTree to a pathlib.Path object.

**Returns:** Path object representing the full path

**Example:**

```python
paths = PathTree(Path("/home/user"))
config = paths.config.app

# Convert to Path
path = config.to_path()  # Path("/home/user/config/app")

# Use with pathlib operations
path.mkdir(parents=True, exist_ok=True)
files = list(path.glob("*.txt"))
```

**Notes:**
- This is when the actual Path object is created
- No filesystem I/O during navigation, only during conversion

---

### `__str__() -> str`

Get string representation of the path.

**Returns:** String representation of the full path

**Example:**

```python
paths = PathTree(Path("/home/user"))
config = paths.config.app

print(str(config))  # "/home/user/config/app"
print(config)  # Same as str(config)
```

---

### `__repr__() -> str`

Get detailed representation for debugging.

**Returns:** String showing PathTree structure

**Example:**

```python
paths = PathTree(Path("/home/user"))
config = paths.config

print(repr(config))
# PathTree(base=PosixPath('/home/user'), segments=('config',))
```

---

## Filesystem Check Methods

### `exists() -> bool`

Check if the path exists in the filesystem.

**Returns:** True if path exists, False otherwise

**Example:**

```python
paths = PathTree(Path("/home/user"))

if paths.config.exists():
    print("Config directory exists")
else:
    print("Config directory does not exist")
```

**Notes:**
- Performs filesystem I/O
- Equivalent to `self.to_path().exists()`

---

### `is_file() -> bool`

Check if the path is a file.

**Returns:** True if path is a file, False otherwise

**Example:**

```python
paths = PathTree(Path("/home/user"))

if paths.config.settings.is_file():
    print("settings is a file")
```

**Notes:**
- Performs filesystem I/O
- Returns False if path doesn't exist
- Equivalent to `self.to_path().is_file()`

---

### `is_dir() -> bool`

Check if the path is a directory.

**Returns:** True if path is a directory, False otherwise

**Example:**

```python
paths = PathTree(Path("/home/user"))

if paths.config.is_dir():
    print("config is a directory")
```

**Notes:**
- Performs filesystem I/O
- Returns False if path doesn't exist
- Equivalent to `self.to_path().is_dir()`

---

## Properties

### `_base: Path`

The base directory path.

**Type:** Path
**Access:** Read-only (frozen dataclass)

**Example:**

```python
paths = PathTree(Path("/home/user"))
print(paths._base)  # PosixPath('/home/user')
```

---

### `_segments: tuple[str, ...]`

The path segments accumulated during navigation.

**Type:** tuple[str, ...]
**Access:** Read-only (frozen dataclass)

**Example:**

```python
paths = PathTree(Path("/home/user"))
config = paths.config.app

print(config._segments)  # ('config', 'app')
```

---

## Usage Patterns

### Pattern 1: Simple Navigation

```python
paths = PathTree(Path("/home/user"))
config_file = paths.config / "settings.json"
```

### Pattern 2: Dynamic Navigation

```python
paths = PathTree(Path("/home/user"))
dir_name = "config"
subdir = "app"

path = paths[dir_name][subdir].to_path()
```

### Pattern 3: Conditional Navigation

```python
paths = PathTree(Path("/home/user"))

if paths.config.exists():
    settings = paths.config / "settings.json"
else:
    settings = paths / "default_settings.json"
```

### Pattern 4: Mixed Navigation

```python
paths = PathTree(Path("/home/user"))

# Mix attribute, bracket, and slash
path = paths.config["app"] / "data" / "file.txt"
```

---

## Type Hints

```python
from pathlib import Path
from filesystem_path_builder import PathTree, Segment

# Constructor
paths: PathTree = PathTree(Path("/home/user"))

# Navigation returns PathTree
config: PathTree = paths.config

# Conversion returns Path
path: Path = config.to_path()

# Checks return bool
exists: bool = config.exists()
```

---

## Thread Safety

PathTree is thread-safe because:
- Immutable (frozen dataclass)
- No mutable state
- Each navigation creates new instance
- No shared mutable data

**Example:**

```python
import threading
from pathlib import Path
from filesystem_path_builder import PathTree

paths = PathTree(Path("/home/user"))

def worker(name: str):
    # Each thread navigates independently
    config = paths.config[name]
    print(config.to_path())

# Safe concurrent access
threads = [
    threading.Thread(target=worker, args=("app1",)),
    threading.Thread(target=worker, args=("app2",)),
]

for t in threads:
    t.start()
for t in threads:
    t.join()
```

---

## Performance Characteristics

- **Navigation:** O(1) per segment (attribute access)
- **Path Building:** O(n) where n = number of segments
- **Memory:** O(s) where s = total segments
- **No I/O:** Navigation doesn't touch filesystem

---

## Limitations

1. **No os.PathLike Support** - PathTree doesn't implement `__fspath__`
   - Use `to_path()` to convert to Path first
   - Or use ManagedPathTree which implements os.PathLike

2. **No Hidden Directory Support** - PathTree doesn't handle dot-prefixed directories
   - Use PathsBuilder + ManagedPathTree for hidden directories

3. **No Validation** - PathTree doesn't validate paths
   - Any attribute access creates a new PathTree
   - Validation happens at filesystem level (when using to_path())

---

## See Also

- [ManagedPathTree](managed_pathtree.md) - Extended PathTree with creation
- [PathsBuilder](builder.md) - Builder for explicit path configuration
- [Usage Patterns](../guides/usage_patterns.md) - Common usage patterns

---

**Next:** [PathsBuilder API](builder.md) | [ManagedPathTree API](managed_pathtree.md)

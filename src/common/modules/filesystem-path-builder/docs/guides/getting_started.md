# Getting Started

This guide will help you get started with the filesystem-path-builder module.

---

## Installation

### As a uv Project Dependency

```bash
uv add filesystem-path-builder
```

### From Source

```bash
cd src/common/modules/filesystem-path-builder
pip install -e .
```

---

## Quick Start

### 1. Import the Module

```python
from pathlib import Path
from filesystem_path_builder import PathTree, PathsBuilder, ManagedPathTree, PathDefinition
```

---

## Basic Usage

### Dynamic Navigation with PathTree

PathTree provides dynamic, attribute-based navigation:

```python
from pathlib import Path
from filesystem_path_builder import PathTree

# Create a PathTree
paths = PathTree(Path("/home/user"))

# Navigate using attributes
config_dir = paths.config
app_dir = paths.config.app
data_dir = paths.data

# Convert to Path when needed
config_path = config_dir.to_path()  # Path("/home/user/config")
app_path = app_dir.to_path()  # Path("/home/user/config/app")

# Use with file operations
settings_file = paths.config / "settings.json"
with open(settings_file.to_path(), 'r') as f:
    settings = f.read()
```

**Key Points:**
- Navigation is lazy (no Path objects created until `to_path()`)
- Immutable (each navigation creates new PathTree)
- No filesystem I/O during navigation

---

### Explicit Building with PathsBuilder

PathsBuilder provides explicit path configuration with hidden directory support:

```python
from pathlib import Path
from filesystem_path_builder import PathsBuilder

# Create a builder
builder = PathsBuilder(Path("/home/user"))

# Add path definitions
builder.add("config.app", hidden=False)
builder.add("data.cache", hidden=True)  # Creates .cache
builder.add("logs", hidden=False)

# Build the ManagedPathTree
paths = builder.build()

# Navigate
config_path = paths.config.app.to_path()  # /home/user/config/app
cache_path = paths.data.cache.to_path()  # /home/user/data/.cache
```

**Key Points:**
- Fluent interface (method chaining)
- Explicit configuration
- Hidden directory support (dot-prefix)
- Builds ManagedPathTree

---

### Bulk Creation with ManagedPathTree

ManagedPathTree combines navigation with bulk directory creation:

```python
from pathlib import Path
from filesystem_path_builder import ManagedPathTree, PathDefinition

# Create with definitions
managed = ManagedPathTree(
    base=Path("/home/user/.myapp"),
    definitions=[
        PathDefinition(key="config", hidden=False),
        PathDefinition(key="data.cache", hidden=False),
        PathDefinition(key="data.logs", hidden=False),
        PathDefinition(key="plugins", hidden=False),
    ]
)

# Create all directories at once
managed.create()

# Navigate
config_dir = managed.config.to_path()  # /home/user/.myapp/config
cache_dir = managed.data.cache.to_path()  # /home/user/.myapp/data/cache
log_file = managed.data.logs / "app.log"  # /home/user/.myapp/data/logs/app.log
```

**Key Points:**
- Combines navigation and creation
- Bulk directory creation
- Registry of path definitions
- Implements os.PathLike

---

## Common Patterns

### Pattern 1: Application Configuration

```python
from pathlib import Path
from filesystem_path_builder import ManagedPathTree, PathDefinition

# Define application structure
app_paths = ManagedPathTree(
    base=Path.home() / ".myapp",
    definitions=[
        PathDefinition(key="config", hidden=False),
        PathDefinition(key="data", hidden=False),
        PathDefinition(key="cache", hidden=False),
        PathDefinition(key="logs", hidden=False),
    ]
)

# Create directories
app_paths.create()

# Use paths
config_file = app_paths.config / "settings.toml"
data_dir = app_paths.data
log_file = app_paths.logs / "app.log"
```

---

### Pattern 2: Hidden Dotfiles

```python
from pathlib import Path
from filesystem_path_builder import PathsBuilder

# Build dotfiles structure
builder = PathsBuilder(Path.home())
dotfiles = (builder
    .add("dotfiles.config", hidden=True)  # ~/.config
    .add("dotfiles.local.share", hidden=True)  # ~/.local/share
    .add("dotfiles.cache", hidden=True)  # ~/.cache
    .build())

# Create directories
dotfiles.create()

# Access hidden directories
config_dir = dotfiles.dotfiles.config.to_path()  # ~/.config
share_dir = dotfiles.dotfiles.local.share.to_path()  # ~/.local/share
```

---

### Pattern 3: Project Structure

```python
from pathlib import Path
from filesystem_path_builder import PathTree

# Navigate project
project = PathTree(Path("/workspace/myproject"))

# Access project paths
src_dir = project.src.to_path()
tests_dir = project.tests.to_path()
docs_dir = project.docs.to_path()

# Use with file operations
main_file = project.src.main / "app.py"
test_file = project.tests.unit / "test_app.py"
```

---

## Navigation Methods

### Attribute Access

```python
paths = PathTree(Path("/home/user"))
config = paths.config  # Attribute access
app = paths.config.app  # Chained attribute access
```

### Bracket Notation

```python
paths = PathTree(Path("/home/user"))
config = paths["config"]  # Bracket notation
app = paths["config"]["app"]  # Chained bracket notation

# Useful for dynamic names
dir_name = "config"
config = paths[dir_name]
```

### Slash Operator

```python
paths = PathTree(Path("/home/user"))
config = paths / "config"  # Slash operator
app = paths / "config" / "app"  # Chained slash operator

# Mix with attribute access
mixed = paths.config / "app"
```

---

## Converting to Path

All navigation methods return PathTree (or ManagedPathTree). Convert to Path when needed:

```python
paths = PathTree(Path("/home/user"))

# Navigation returns PathTree
config = paths.config  # PathTree

# Convert to Path
config_path = config.to_path()  # Path

# Or use directly with /
config_file = paths.config / "settings.json"
config_file_path = config_file.to_path()  # Path
```

---

## Filesystem Operations

### Check Existence

```python
paths = PathTree(Path("/home/user"))

if paths.config.exists():
    print("Config directory exists")

if paths.config.settings.is_file():
    print("Settings file exists")

if paths.data.is_dir():
    print("Data directory exists")
```

### Create Directories

```python
# With PathTree - manual creation
paths = PathTree(Path("/home/user"))
config_path = paths.config.to_path()
config_path.mkdir(parents=True, exist_ok=True)

# With ManagedPathTree - bulk creation
managed = ManagedPathTree(
    base=Path("/home/user"),
    definitions=[PathDefinition(key="config", hidden=False)]
)
managed.create()  # Creates all defined directories
```

---

## Environment Variables

Paths are automatically expanded:

```python
from pathlib import Path
from filesystem_path_builder import PathTree

# $HOME expansion
paths = PathTree(Path("$HOME/myapp"))  # Expands to /home/user/myapp

# ~ expansion
paths = PathTree(Path("~/myapp"))  # Expands to /home/user/myapp

# Custom environment variables
import os
os.environ["MYAPP_HOME"] = "/opt/myapp"
paths = PathTree(Path("$MYAPP_HOME/config"))  # Expands to /opt/myapp/config
```

---

## Type Hints

```python
from pathlib import Path
from filesystem_path_builder import PathTree, ManagedPathTree, PathsBuilder, PathDefinition

# PathTree
paths: PathTree = PathTree(Path("/home/user"))
config: PathTree = paths.config
config_path: Path = config.to_path()

# PathsBuilder
builder: PathsBuilder = PathsBuilder(Path("/home/user"))
managed: ManagedPathTree = builder.build()

# PathDefinition
definition: PathDefinition = PathDefinition(key="config", hidden=False)
```

---

## Best Practices

### 1. Use PathTree for Simple Navigation

```python
# Good: Simple navigation
paths = PathTree(Path("/home/user"))
config = paths.config.to_path()
```

### 2. Use PathsBuilder for Hidden Directories

```python
# Good: Explicit hidden directory configuration
builder = PathsBuilder(Path.home())
dotfiles = builder.add("dotfiles.config", hidden=True).build()
```

### 3. Use ManagedPathTree for Bulk Creation

```python
# Good: Create multiple directories at once
managed = ManagedPathTree(base=Path("/home/user"), definitions=[...])
managed.create()
```

### 4. Convert to Path for Filesystem Operations

```python
# Good: Convert to Path for operations
paths = PathTree(Path("/home/user"))
config_path = paths.config.to_path()
config_path.mkdir(parents=True, exist_ok=True)

# Bad: Don't try to use PathTree directly with os functions
# os.listdir(paths.config)  # Error: PathTree doesn't implement os.PathLike
```

### 5. Use ManagedPathTree with os Functions

```python
# Good: ManagedPathTree implements os.PathLike
managed = ManagedPathTree(base=Path("/home/user"), definitions=[...])
files = os.listdir(managed)  # Works via __fspath__
```

---

## Common Mistakes

### Mistake 1: Forgetting to Convert to Path

```python
# Wrong
paths = PathTree(Path("/home/user"))
paths.config.mkdir()  # Error: PathTree has no mkdir method

# Correct
paths = PathTree(Path("/home/user"))
paths.config.to_path().mkdir(parents=True, exist_ok=True)
```

### Mistake 2: Using PathTree with os Functions

```python
# Wrong
paths = PathTree(Path("/home/user"))
os.listdir(paths.config)  # Error: PathTree doesn't implement os.PathLike

# Correct (option 1)
paths = PathTree(Path("/home/user"))
os.listdir(paths.config.to_path())

# Correct (option 2)
managed = ManagedPathTree(base=Path("/home/user"), definitions=[...])
os.listdir(managed)  # Works via __fspath__
```

### Mistake 3: Modifying PathTree

```python
# Wrong
paths = PathTree(Path("/home/user"))
paths._base = Path("/other")  # Error: frozen dataclass

# Correct: Create new PathTree
paths = PathTree(Path("/other"))
```

---

## Next Steps

- [Usage Patterns](usage_patterns.md) - Common patterns and best practices
- [Integration Guide](integration.md) - Integration with other libraries
- [API Reference](../api/pathtree.md) - Detailed API documentation
- [Troubleshooting](../reference/troubleshooting.md) - Common issues and solutions

---

**Quick Reference:**

| Task | Use |
|------|-----|
| Simple navigation | PathTree |
| Hidden directories | PathsBuilder |
| Bulk creation | ManagedPathTree |
| os.PathLike support | ManagedPathTree |
| Dynamic navigation | PathTree |
| Explicit configuration | PathsBuilder |


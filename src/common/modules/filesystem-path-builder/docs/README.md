# filesystem-path-builder Documentation

**Version:** 0.1.0
**Python:** >=3.12
**Dependencies:** None (stdlib only)
**License:** MIT

---

## Overview

The `filesystem-path-builder` module provides a flexible, type-safe system for managing filesystem paths with support for dynamic navigation, explicit path building, and bulk directory creation. It's designed for applications that need to manage complex directory structures with features like hidden directories and environment variable expansion.

### Key Features

- **Zero Dependencies** - Uses only Python standard library
- **Type-Safe** - Full type hints with mypy compatibility
- **Immutable Design** - Frozen dataclasses for thread safety
- **Flexible Navigation** - Attribute chaining, bracket notation, and slash operator
- **Strict Mode** - Optional enforcement of explicit path registration to catch typos
- **Key Sanitization** - Automatic normalization of path keys for Python attribute access
- **Hidden Directory Support** - Unix-style dot-prefixed directories
- **Bulk Creation** - Create entire directory trees at once
- **PathLib Integration** - Seamless integration with pathlib.Path
- **Environment Variables** - Automatic expansion of $HOME, ~, etc.

### Core Components

1. **PathTree** - Immutable, dynamic path navigation
2. **PathsBuilder** - Builder pattern for explicit path configuration
3. **ManagedPathTree** - Extended PathTree with registry and bulk creation
4. **PathDefinition** - Simple dataclass for path definitions

---

## Quick Start

### Installation

```python
# As a uv project dependency
uv add filesystem-path-builder

# Or install from source
cd src/common/modules/filesystem-path-builder
pip install -e .
```

### Basic Usage

```python
from pathlib import Path
from filesystem_path_builder import PathTree, PathsBuilder, ManagedPathTree

# Dynamic navigation with PathTree
paths = PathTree(Path("/home/user"))
config_file = paths.config.app / "settings.json"
# Result: /home/user/config/app/settings.json

# Explicit building with PathsBuilder
builder = PathsBuilder(Path("/home/user"))
builder.add_path("config.app", hidden=False)
builder.add_path("data.cache", hidden=True)  # Creates .cache
paths = builder.build()

# Strict mode for production (catches typos)
builder = PathsBuilder(Path("/home/user"), strict=True)
builder.add_path("config", hidden=False)
builder.add_path("data", hidden=False)
paths = builder.build()
# paths.config.path  # OK - registered
# paths.typo.path    # AttributeError - not registered

# Bulk creation with ManagedPathTree
managed = ManagedPathTree(
    base=Path("/home/user"),
    definitions=[
        PathDefinition(key="config.app", hidden=False),
        PathDefinition(key="data.cache", hidden=True),
    ]
)
managed.create()  # Creates all directories at once
```

---

## Documentation Structure

### Architecture Documentation

- **[Architecture Overview](architecture/overview.md)** - System design and principles
- **[Design Patterns](architecture/design_patterns.md)** - Patterns used in the module
- **[Class Hierarchy](architecture/class_hierarchy.md)** - Class relationships and inheritance

### API Reference

- **[PathTree API](api/pathtree.md)** - Dynamic navigation class
- **[PathsBuilder API](api/builder.md)** - Explicit path builder
- **[ManagedPathTree API](api/managed_pathtree.md)** - Extended PathTree with bulk creation
- **[PathDefinition API](api/path_definition.md)** - Path configuration dataclass

### Usage Guides

- **[Getting Started](guides/getting_started.md)** - Quick start and basic usage
- **[Usage Patterns](guides/usage_patterns.md)** - Common patterns and best practices
- **[Integration Guide](guides/integration.md)** - Integration with other libraries
- **[Best Practices](guides/best_practices.md)** - Recommendations and anti-patterns

### Reference

- **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions
- **[Code Examples](reference/examples.md)** - Comprehensive code examples
- **[Testing Guide](reference/testing.md)** - Testing strategies and examples

---

## Common Use Cases

### 1. Application Configuration Directories

```python
from pathlib import Path
from filesystem_path_builder import ManagedPathTree, PathDefinition

# Define application directory structure
app_paths = ManagedPathTree(
    base=Path.home() / ".myapp",
    definitions=[
        PathDefinition(key="config", hidden=False),
        PathDefinition(key="data.cache", hidden=False),
        PathDefinition(key="data.logs", hidden=False),
        PathDefinition(key="plugins", hidden=False),
    ]
)

# Create all directories
app_paths.create()

# Access paths
config_file = app_paths.config / "settings.toml"
cache_dir = app_paths.data.cache
log_file = app_paths.data.logs / "app.log"
```

### 2. Hidden Dotfiles Management

```python
from pathlib import Path
from filesystem_path_builder import PathsBuilder

# Build dotfiles structure with hidden directories
builder = PathsBuilder(Path.home())
builder.add("dotfiles.config", hidden=True)  # Creates ~/.config
builder.add("dotfiles.local.share", hidden=True)  # Creates ~/.local/share
builder.add("dotfiles.cache", hidden=True)  # Creates ~/.cache

dotfiles = builder.build()

# Access hidden directories
config_dir = dotfiles.dotfiles.config  # ~/.config
share_dir = dotfiles.dotfiles.local.share  # ~/.local/share
```

### 3. Project Directory Structure

```python
from pathlib import Path
from filesystem_path_builder import PathTree

# Navigate project structure dynamically
project = PathTree(Path("/workspace/myproject"))

# Access various project paths
src_dir = project.src
tests_dir = project.tests
docs_dir = project.docs
build_dir = project.build.output

# Use with file operations
source_file = project.src.main / "app.py"
test_file = project.tests.unit / "test_app.py"
```

---

## Module Statistics

- **Total Source Lines:** ~871 lines
- **Total Test Lines:** ~507 lines
- **Test Coverage:** Comprehensive (PathTree, PathsBuilder, ManagedPathTree)
- **Type Coverage:** 100% (all public APIs fully typed)
- **Dependencies:** 0 (stdlib only)

---

## Design Philosophy

### Immutability

All core classes use frozen dataclasses to ensure immutability and thread safety. Once created, path structures cannot be modified, preventing accidental mutations.

### Type Safety

Full type hints throughout the codebase with mypy compatibility. The `Segment` type alias (`Union[str, Path]`) provides flexibility while maintaining type safety.

### Separation of Concerns

- **PathTree** - Pure navigation (no creation)
- **PathsBuilder** - Explicit configuration (builder pattern)
- **ManagedPathTree** - Navigation + creation (combines both)

### Zero Dependencies

Uses only Python standard library (pathlib, os, dataclasses) to minimize dependency overhead and ensure compatibility.

---

## Performance Characteristics

- **Memory Efficient** - Uses `__slots__` to reduce memory footprint
- **Thread-Safe** - Immutable design allows safe concurrent access
- **Lazy Evaluation** - Path objects created on-demand during navigation
- **No I/O in Navigation** - PathTree navigation doesn't touch filesystem

---

## Known Limitations

1. **PathNamespace Reference** - Test file references old `PathNamespace` name (should be `ManagedPathTree`)
2. **Overlapping Paths** - When paths overlap, first definition wins (no merging)
3. **os.PathLike Support** - Only `ManagedPathTree` implements `__fspath__`, not `PathTree`

---

## Contributing

See the main project README for contribution guidelines.

---

## License

MIT License - See LICENSE file for details.

---

## Related Documentation

- **[Investigation Notes](helpers/INVESTIGATION_NOTES.md)** - Comprehensive investigation findings (2652 lines)
- **[Requirements Checklist](helpers/REQUIREMENTS_CHECKLIST.md)** - Investigation task tracking
- **[Session Summary](helpers/SESSION_SUMMARY.md)** - Investigation accomplishments

---

**Last Updated:** 2025-11-06
**Documentation Version:** 1.1
**Module Version:** 0.1.0

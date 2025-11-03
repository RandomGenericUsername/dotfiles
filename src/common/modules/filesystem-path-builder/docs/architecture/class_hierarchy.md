# Class Hierarchy

This document describes the class relationships and inheritance hierarchy in the filesystem-path-builder module.

---

## Class Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Segment                              │
│                   (Type Alias)                               │
│                   Union[str, Path]                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ used by
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       PathTree                               │
│                  (Base Navigation)                           │
├─────────────────────────────────────────────────────────────┤
│ - _base: Path                                                │
│ - _segments: tuple[str, ...]                                 │
├─────────────────────────────────────────────────────────────┤
│ + __getattr__(name: str) -> PathTree                         │
│ + __getitem__(key: str) -> PathTree                          │
│ + __truediv__(other: Segment) -> PathTree                    │
│ + to_path() -> Path                                          │
│ + exists() -> bool                                           │
│ + is_file() -> bool                                          │
│ + is_dir() -> bool                                           │
└─────────────────────────────────────────────────────────────┘
                            △
                            │ extends
                            │
┌─────────────────────────────────────────────────────────────┐
│                   ManagedPathTree                            │
│            (Navigation + Creation)                           │
├─────────────────────────────────────────────────────────────┤
│ - _definitions: tuple[PathDefinition, ...]                   │
├─────────────────────────────────────────────────────────────┤
│ + create(parents: bool, exist_ok: bool) -> None              │
│ + __fspath__() -> str                                        │
│ + _build_path(definition: PathDefinition) -> Path            │
│ + _parse_key(key: str) -> list[str]                          │
└─────────────────────────────────────────────────────────────┘
                            △
                            │ creates
                            │
┌─────────────────────────────────────────────────────────────┐
│                     PathsBuilder                             │
│                  (Builder Pattern)                           │
├─────────────────────────────────────────────────────────────┤
│ - _base: Path                                                │
│ - _definitions: list[PathDefinition]                         │
├─────────────────────────────────────────────────────────────┤
│ + add(key: str, hidden: bool) -> Self                        │
│ + build() -> ManagedPathTree                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   PathDefinition                             │
│                  (Value Object)                              │
├─────────────────────────────────────────────────────────────┤
│ + key: str                                                   │
│ + hidden: bool = False                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Inheritance Hierarchy

### PathTree (Base Class)

**Type:** Frozen dataclass with slots
**Purpose:** Base navigation functionality
**Inheritance:** None (root class)

```python
@dataclass(frozen=True, slots=True)
class PathTree:
    _base: Path
    _segments: tuple[str, ...] = field(default_factory=tuple)
```

**Responsibilities:**
- Dynamic attribute-based navigation
- Bracket notation support
- Slash operator support
- Path conversion
- File/directory checks

**Subclasses:**
- ManagedPathTree

---

### ManagedPathTree (Derived Class)

**Type:** Frozen dataclass with slots
**Purpose:** Extends PathTree with creation and registry
**Inheritance:** Extends PathTree

```python
@dataclass(frozen=True, slots=True)
class ManagedPathTree(PathTree):
    _definitions: tuple[PathDefinition, ...] = field(default_factory=tuple)
```

**Inherited from PathTree:**
- All navigation methods (`__getattr__`, `__getitem__`, `__truediv__`)
- Path conversion (`to_path()`)
- File/directory checks (`exists()`, `is_file()`, `is_dir()`)

**Additional Responsibilities:**
- Bulk directory creation
- Path definition registry
- Hidden directory support
- os.PathLike protocol

**Overridden Methods:**
- `__getattr__` - Returns ManagedPathTree instead of PathTree
- `__getitem__` - Returns ManagedPathTree instead of PathTree
- `__truediv__` - Returns ManagedPathTree instead of PathTree

---

### PathsBuilder (Independent Class)

**Type:** Regular class (not frozen)
**Purpose:** Build ManagedPathTree instances
**Inheritance:** None

```python
class PathsBuilder:
    def __init__(self, base: Segment) -> None:
        self._base = Path(base).expanduser().resolve()
        self._definitions: list[PathDefinition] = []
```

**Responsibilities:**
- Collect path definitions
- Validate path keys
- Build ManagedPathTree instances
- Provide fluent interface

**Relationship to ManagedPathTree:**
- Factory: Creates ManagedPathTree via `build()` method
- Not related by inheritance

---

### PathDefinition (Value Object)

**Type:** Frozen dataclass with slots
**Purpose:** Store path configuration
**Inheritance:** None

```python
@dataclass(frozen=True, slots=True)
class PathDefinition:
    key: str
    hidden: bool = False
```

**Responsibilities:**
- Store path key (dot-separated)
- Store hidden status
- Immutable value object

**Relationship to Other Classes:**
- Used by PathsBuilder (stored in list)
- Used by ManagedPathTree (stored in tuple)

---

## Type Relationships

### Segment Type Alias

```python
Segment = Union[str, Path]
```

**Used By:**
- `PathTree.__init__(base: Segment)`
- `PathTree.__truediv__(other: Segment)`
- `PathsBuilder.__init__(base: Segment)`

**Purpose:**
- Flexible input (accept str or Path)
- Type safety (Union type)
- Convenience (no manual conversion)

---

## Method Inheritance

### PathTree Methods

All methods available in PathTree:

```python
# Navigation
__getattr__(name: str) -> PathTree
__getitem__(key: str) -> PathTree
__truediv__(other: Segment) -> PathTree

# Conversion
to_path() -> Path
__str__() -> str
__repr__() -> str

# Checks
exists() -> bool
is_file() -> bool
is_dir() -> bool
```

### ManagedPathTree Methods

Inherits all PathTree methods plus:

```python
# Creation
create(*, parents: bool = True, exist_ok: bool = True) -> None

# Protocol
__fspath__() -> str

# Internal
_build_path(definition: PathDefinition) -> Path
_parse_key(key: str) -> list[str]

# Overridden (return ManagedPathTree instead of PathTree)
__getattr__(name: str) -> ManagedPathTree
__getitem__(key: str) -> ManagedPathTree
__truediv__(other: Segment) -> ManagedPathTree
```

---

## Composition Relationships

### PathsBuilder Composition

```python
PathsBuilder
    ├── _base: Path (composition)
    └── _definitions: list[PathDefinition] (composition)
```

**Lifetime:**
- PathDefinitions created during `add()` calls
- PathDefinitions owned by PathsBuilder
- Converted to tuple when building ManagedPathTree

### ManagedPathTree Composition

```python
ManagedPathTree
    ├── _base: Path (inherited from PathTree)
    ├── _segments: tuple[str, ...] (inherited from PathTree)
    └── _definitions: tuple[PathDefinition, ...] (own field)
```

**Lifetime:**
- PathDefinitions passed from PathsBuilder
- PathDefinitions immutable (tuple)
- PathDefinitions owned by ManagedPathTree

---

## Protocol Implementation

### os.PathLike Protocol

```python
class os.PathLike(Protocol[AnyStr]):
    def __fspath__(self) -> AnyStr: ...
```

**Implemented By:**
- ManagedPathTree (returns str)

**Not Implemented By:**
- PathTree (no __fspath__ method)
- PathsBuilder (not a path object)
- PathDefinition (configuration, not a path)

**Usage:**

```python
managed = ManagedPathTree(...)

# Works with os functions
os.listdir(managed)

# Works with pathlib
Path(managed)

# Works with open
with open(managed / "file.txt") as f:
    pass
```

---

## Dataclass Features

### Frozen Dataclasses

All core classes except PathsBuilder are frozen:

```python
@dataclass(frozen=True, slots=True)
class PathTree: ...

@dataclass(frozen=True, slots=True)
class ManagedPathTree(PathTree): ...

@dataclass(frozen=True, slots=True)
class PathDefinition: ...
```

**Benefits:**
- Immutable (cannot modify after creation)
- Hashable (can use in sets, dict keys)
- Thread-safe (safe concurrent access)
- Memory-efficient (`__slots__`)

### Mutable Class

Only PathsBuilder is mutable:

```python
class PathsBuilder:
    def __init__(self, base: Segment) -> None:
        self._base = Path(base).expanduser().resolve()
        self._definitions: list[PathDefinition] = []
```

**Reason:**
- Builder pattern requires mutation during building
- Not meant to be shared or persisted
- Converted to immutable ManagedPathTree via `build()`

---

## Class Responsibilities Summary

| Class | Responsibility | Mutable | Inheritance |
|-------|---------------|---------|-------------|
| PathTree | Navigation | No | None |
| ManagedPathTree | Navigation + Creation | No | Extends PathTree |
| PathsBuilder | Building | Yes | None |
| PathDefinition | Configuration | No | None |

---

## Dependency Graph

```
User Code
    │
    ├─→ PathTree (direct usage)
    │       └─→ Path (stdlib)
    │
    ├─→ PathsBuilder (building)
    │       ├─→ PathDefinition (creates)
    │       ├─→ ManagedPathTree (creates)
    │       └─→ Path (stdlib)
    │
    └─→ ManagedPathTree (direct usage)
            ├─→ PathTree (extends)
            ├─→ PathDefinition (uses)
            └─→ Path (stdlib)
```

**External Dependencies:**
- `pathlib.Path` (stdlib)
- `dataclasses` (stdlib)
- `os` (stdlib)

**No Third-Party Dependencies**

---

## Type Hierarchy

```
object
    │
    ├─→ PathTree (frozen dataclass)
    │       └─→ ManagedPathTree (frozen dataclass)
    │
    ├─→ PathsBuilder (regular class)
    │
    └─→ PathDefinition (frozen dataclass)

Union[str, Path]  (Segment type alias)
```

---

## Interface Contracts

### PathTree Contract

```python
# Navigation always returns new PathTree
paths.config.app  # Returns PathTree, not Path

# Conversion to Path is explicit
paths.config.app.to_path()  # Returns Path

# Immutable - cannot modify
# paths._base = ...  # Error: frozen dataclass
```

### ManagedPathTree Contract

```python
# Inherits PathTree contract
# Navigation returns ManagedPathTree (not PathTree)

# Additional: Can create directories
managed.create()  # Creates all defined directories

# Additional: Implements os.PathLike
os.listdir(managed)  # Works via __fspath__
```

### PathsBuilder Contract

```python
# Fluent interface - methods return self
builder.add("config").add("data")  # Chaining works

# Build returns ManagedPathTree
managed = builder.build()  # Returns ManagedPathTree

# Mutable - can add definitions
builder.add("new")  # Modifies builder
```

---

**Next:** [Back to Overview](overview.md) | [Design Patterns](design_patterns.md)

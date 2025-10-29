# Architecture Overview

## System Design

The `filesystem-path-builder` module is designed around three core abstractions that work together to provide flexible filesystem path management:

1. **PathTree** - Dynamic, immutable path navigation
2. **PathsBuilder** - Explicit path configuration using builder pattern
3. **ManagedPathTree** - Combines navigation with bulk directory creation

### Design Principles

#### 1. Immutability

All core classes are frozen dataclasses, ensuring:
- Thread-safe concurrent access
- Predictable behavior (no hidden mutations)
- Safe sharing across components
- Memory efficiency through `__slots__`

#### 2. Type Safety

Complete type coverage with:
- Full type hints on all public APIs
- mypy compatibility
- `Segment` type alias for flexible input (`Union[str, Path]`)
- Proper return type annotations

#### 3. Separation of Concerns

Each class has a single, well-defined responsibility:
- **PathTree**: Navigation only (no filesystem operations)
- **PathsBuilder**: Configuration only (builder pattern)
- **ManagedPathTree**: Navigation + creation (combines both)

#### 4. Zero Dependencies

Uses only Python standard library:
- `pathlib` for path operations
- `dataclasses` for data structures
- `os` for filesystem operations
- No external dependencies

---

## Component Architecture

### PathTree - Dynamic Navigation

**Purpose:** Provide dynamic, attribute-based navigation through directory structures.

**Key Features:**
- Immutable (frozen dataclass)
- Dynamic attribute access (`paths.foo.bar`)
- Bracket notation (`paths["foo"]`)
- Slash operator (`paths / "foo"`)
- No filesystem I/O during navigation

**Design Pattern:** Flyweight pattern - creates path objects on-demand

```python
@dataclass(frozen=True, slots=True)
class PathTree:
    _base: Path
    _segments: tuple[str, ...] = field(default_factory=tuple)
```

**Navigation Flow:**
```
PathTree(base="/home/user")
    ↓ attribute access: .config
PathTree(base="/home/user", segments=("config",))
    ↓ attribute access: .app
PathTree(base="/home/user", segments=("config", "app"))
    ↓ convert to Path
Path("/home/user/config/app")
```

### PathsBuilder - Explicit Configuration

**Purpose:** Build path structures explicitly with control over hidden directories.

**Key Features:**
- Builder pattern for fluent API
- Explicit path definitions
- Hidden directory support (dot-prefix)
- Validation of path keys
- Builds ManagedPathTree

**Design Pattern:** Builder pattern with fluent interface

```python
class PathsBuilder:
    def __init__(self, base: Segment) -> None
    def add(self, key: str, *, hidden: bool = False) -> Self
    def build(self) -> ManagedPathTree
```

**Building Flow:**
```
PathsBuilder(base="/home/user")
    ↓ add("config.app", hidden=False)
PathsBuilder with [PathDefinition("config.app", False)]
    ↓ add("data.cache", hidden=True)
PathsBuilder with [PathDefinition("config.app", False), PathDefinition("data.cache", True)]
    ↓ build()
ManagedPathTree with registry and navigation
```

### ManagedPathTree - Navigation + Creation

**Purpose:** Combine dynamic navigation with bulk directory creation and registry management.

**Key Features:**
- Extends PathTree (inherits navigation)
- Registry of path definitions
- Bulk directory creation
- Hidden directory support
- os.PathLike protocol support

**Design Pattern:** Composite pattern - combines PathTree navigation with creation logic

```python
@dataclass(frozen=True, slots=True)
class ManagedPathTree(PathTree):
    _definitions: tuple[PathDefinition, ...] = field(default_factory=tuple)
    
    def create(self, *, parents: bool = True, exist_ok: bool = True) -> None
    def __fspath__(self) -> str
```

**Creation Flow:**
```
ManagedPathTree(base="/home/user", definitions=[...])
    ↓ create()
For each PathDefinition:
    ↓ parse key "config.app"
    ["config", "app"]
    ↓ apply hidden rules
    [("config", False), ("app", False)]
    ↓ build path
    Path("/home/user/config/app")
    ↓ create directory
    mkdir -p /home/user/config/app
```

### PathDefinition - Configuration Data

**Purpose:** Store path configuration (key and hidden status).

**Key Features:**
- Simple dataclass
- Immutable (frozen)
- Validation in PathsBuilder

```python
@dataclass(frozen=True, slots=True)
class PathDefinition:
    key: str
    hidden: bool = False
```

---

## Data Flow

### 1. Dynamic Navigation (PathTree)

```
User Code
    ↓ paths.config.app
PathTree.__getattr__("config")
    ↓ create new PathTree with segment
PathTree(segments=("config",))
    ↓ .app
PathTree.__getattr__("app")
    ↓ create new PathTree with segment
PathTree(segments=("config", "app"))
    ↓ convert to Path
Path("/home/user/config/app")
```

### 2. Explicit Building (PathsBuilder)

```
User Code
    ↓ builder.add("config.app")
PathsBuilder.add()
    ↓ create PathDefinition
PathDefinition(key="config.app", hidden=False)
    ↓ store in list
builder._definitions.append(...)
    ↓ builder.build()
PathsBuilder.build()
    ↓ create ManagedPathTree
ManagedPathTree(base=..., definitions=...)
```

### 3. Bulk Creation (ManagedPathTree)

```
User Code
    ↓ managed.create()
ManagedPathTree.create()
    ↓ for each definition
PathDefinition(key="config.app", hidden=False)
    ↓ parse key
["config", "app"]
    ↓ apply hidden rules
[("config", False), ("app", False)]
    ↓ build path
Path("/home/user/config/app")
    ↓ create directory
path.mkdir(parents=True, exist_ok=True)
```

---

## Type System

### Core Types

```python
# Type alias for flexible input
Segment = Union[str, Path]

# Core classes
PathTree: Immutable navigation
PathsBuilder: Mutable builder
ManagedPathTree: Immutable navigation + creation
PathDefinition: Immutable configuration
```

### Type Relationships

```
Segment (Union[str, Path])
    ↓ used by
PathTree.__init__(base: Segment)
PathsBuilder.__init__(base: Segment)
    ↓ creates
ManagedPathTree (extends PathTree)
    ↓ contains
PathDefinition (frozen dataclass)
```

---

## Hidden Directory Mechanism

### How It Works

1. **Definition Level** - Hidden status stored in PathDefinition
2. **Parsing Level** - Key split into segments ("config.app" → ["config", "app"])
3. **Application Level** - Hidden status applied to final segment only
4. **Building Level** - Dot prefix added to hidden directories

### Example

```python
PathDefinition(key="config.app", hidden=True)
    ↓ parse key
["config", "app"]
    ↓ apply hidden to final segment
[("config", False), ("app", True)]
    ↓ build path
Path("/home/user/config/.app")  # Only "app" is hidden
```

### Registry-Based Approach

ManagedPathTree maintains a registry of all path definitions, allowing sophisticated hidden directory handling:

```python
definitions = [
    PathDefinition(key="config", hidden=False),
    PathDefinition(key="config.app", hidden=True),
]
# Result: /home/user/config/.app
# "config" is not hidden, "app" is hidden
```

---

## Memory Efficiency

### Slots Usage

All classes use `__slots__` to reduce memory footprint:

```python
@dataclass(frozen=True, slots=True)
class PathTree:
    _base: Path
    _segments: tuple[str, ...] = field(default_factory=tuple)
```

**Benefits:**
- Reduced memory per instance (~40% savings)
- Faster attribute access
- Prevents accidental attribute creation

### Immutable Collections

Uses tuples instead of lists for immutability and memory efficiency:

```python
_segments: tuple[str, ...]  # Immutable, memory-efficient
_definitions: tuple[PathDefinition, ...]  # Immutable, memory-efficient
```

---

## Thread Safety

### Immutability Guarantees

All core classes are frozen, ensuring:
- No mutation after creation
- Safe concurrent reads
- No locks needed for read operations

### Safe Patterns

```python
# Safe: Multiple threads can navigate concurrently
paths = PathTree(Path("/home/user"))
thread1: path1 = paths.config.app
thread2: path2 = paths.data.cache
# No conflicts - each navigation creates new immutable objects

# Safe: Multiple threads can create directories
managed = ManagedPathTree(...)
thread1: managed.create()
thread2: managed.create()
# Safe due to exist_ok=True default
```

---

## Extension Points

### 1. Custom Navigation

Extend PathTree for custom navigation logic:

```python
class CustomPathTree(PathTree):
    def __getattr__(self, name: str) -> "CustomPathTree":
        # Custom logic here
        return super().__getattr__(name)
```

### 2. Custom Building

Extend PathsBuilder for custom configuration:

```python
class CustomBuilder(PathsBuilder):
    def add_hidden(self, key: str) -> Self:
        return self.add(key, hidden=True)
```

### 3. Custom Creation

Extend ManagedPathTree for custom creation logic:

```python
class CustomManagedTree(ManagedPathTree):
    def create(self, *, mode: int = 0o755, **kwargs) -> None:
        # Custom creation logic
        super().create(**kwargs)
```

---

## Performance Characteristics

- **Navigation:** O(1) per segment (attribute access)
- **Path Building:** O(n) where n = number of segments
- **Directory Creation:** O(m) where m = number of definitions
- **Memory:** O(s) where s = total segments across all paths

---

## Design Trade-offs

### Immutability vs Flexibility

**Choice:** Immutability  
**Trade-off:** Cannot modify after creation, but gains thread safety and predictability

### Dynamic vs Explicit

**Choice:** Support both (PathTree for dynamic, PathsBuilder for explicit)  
**Trade-off:** More classes, but better separation of concerns

### Registry vs Direct

**Choice:** Registry-based (ManagedPathTree stores definitions)  
**Trade-off:** More memory, but enables sophisticated hidden directory handling

---

**Next:** [Design Patterns](design_patterns.md) | [Class Hierarchy](class_hierarchy.md)


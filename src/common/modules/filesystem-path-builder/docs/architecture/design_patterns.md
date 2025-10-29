# Design Patterns

This document describes the design patterns used in the filesystem-path-builder module.

---

## 1. Builder Pattern

### Implementation: PathsBuilder

The Builder pattern is used to construct complex `ManagedPathTree` objects step-by-step.

### Structure

```python
class PathsBuilder:
    def __init__(self, base: Segment) -> None:
        self._base = Path(base).expanduser().resolve()
        self._definitions: list[PathDefinition] = []
    
    def add(self, key: str, *, hidden: bool = False) -> Self:
        """Add a path definition (fluent interface)"""
        self._definitions.append(PathDefinition(key=key, hidden=hidden))
        return self
    
    def build(self) -> ManagedPathTree:
        """Build the final ManagedPathTree"""
        return ManagedPathTree(
            base=self._base,
            definitions=tuple(self._definitions)
        )
```

### Benefits

- **Fluent Interface**: Method chaining for readable configuration
- **Separation**: Building logic separate from the final object
- **Validation**: Can validate during building phase
- **Flexibility**: Easy to add new configuration options

### Usage Example

```python
builder = PathsBuilder(Path("/home/user"))
paths = (builder
    .add("config.app", hidden=False)
    .add("data.cache", hidden=True)
    .add("logs", hidden=False)
    .build())
```

---

## 2. Flyweight Pattern

### Implementation: PathTree Navigation

The Flyweight pattern is used to minimize memory usage by sharing path segments and creating path objects on-demand.

### Structure

```python
@dataclass(frozen=True, slots=True)
class PathTree:
    _base: Path
    _segments: tuple[str, ...] = field(default_factory=tuple)
    
    def __getattr__(self, name: str) -> "PathTree":
        """Create new PathTree with additional segment"""
        return PathTree(
            base=self._base,
            segments=self._segments + (name,)
        )
```

### Benefits

- **Memory Efficient**: Shares base path across all navigation steps
- **Lazy Creation**: Path objects created only when needed
- **Immutable**: Each navigation step creates new immutable object
- **No I/O**: Navigation doesn't touch filesystem

### Usage Example

```python
paths = PathTree(Path("/home/user"))
# No Path objects created yet

config = paths.config
# PathTree(base="/home/user", segments=("config",))

app = paths.config.app
# PathTree(base="/home/user", segments=("config", "app"))

final_path = app.to_path()
# Path("/home/user/config/app") - created on-demand
```

---

## 3. Composite Pattern

### Implementation: ManagedPathTree

The Composite pattern combines PathTree navigation with directory creation capabilities.

### Structure

```python
@dataclass(frozen=True, slots=True)
class ManagedPathTree(PathTree):
    """Combines navigation (from PathTree) with creation"""
    _definitions: tuple[PathDefinition, ...] = field(default_factory=tuple)
    
    def create(self, *, parents: bool = True, exist_ok: bool = True) -> None:
        """Add creation capability"""
        for definition in self._definitions:
            path = self._build_path(definition)
            path.mkdir(parents=parents, exist_ok=exist_ok)
```

### Benefits

- **Inheritance**: Reuses PathTree navigation logic
- **Extension**: Adds creation without modifying PathTree
- **Single Interface**: Navigation and creation in one object
- **Separation**: Can still use PathTree alone for navigation-only

### Usage Example

```python
# Use as PathTree (navigation)
managed = ManagedPathTree(base=Path("/home/user"), definitions=[...])
config_path = managed.config.app.to_path()

# Use creation capability
managed.create()  # Creates all defined directories
```

---

## 4. Immutable Object Pattern

### Implementation: All Core Classes

All core classes use frozen dataclasses to ensure immutability.

### Structure

```python
@dataclass(frozen=True, slots=True)
class PathTree:
    _base: Path
    _segments: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True, slots=True)
class PathDefinition:
    key: str
    hidden: bool = False

@dataclass(frozen=True, slots=True)
class ManagedPathTree(PathTree):
    _definitions: tuple[PathDefinition, ...] = field(default_factory=tuple)
```

### Benefits

- **Thread Safety**: Safe concurrent access without locks
- **Predictability**: Cannot be modified after creation
- **Hashable**: Can be used as dict keys or in sets
- **Memory Efficient**: `__slots__` reduces memory footprint

### Usage Example

```python
paths = PathTree(Path("/home/user"))
# paths._base = Path("/other")  # Error: frozen dataclass

# Safe concurrent access
thread1: path1 = paths.config
thread2: path2 = paths.data
# No conflicts - immutable
```

---

## 5. Factory Method Pattern

### Implementation: PathsBuilder.build()

The Factory Method pattern is used to create ManagedPathTree instances.

### Structure

```python
class PathsBuilder:
    def build(self) -> ManagedPathTree:
        """Factory method to create ManagedPathTree"""
        return ManagedPathTree(
            base=self._base,
            definitions=tuple(self._definitions)
        )
```

### Benefits

- **Encapsulation**: Creation logic hidden in builder
- **Flexibility**: Can change creation logic without affecting clients
- **Validation**: Can validate before creating
- **Type Safety**: Returns specific type (ManagedPathTree)

### Usage Example

```python
builder = PathsBuilder(Path("/home/user"))
builder.add("config", hidden=False)

# Factory method creates the final object
managed = builder.build()
```

---

## 6. Fluent Interface Pattern

### Implementation: PathsBuilder

The Fluent Interface pattern provides method chaining for readable configuration.

### Structure

```python
class PathsBuilder:
    def add(self, key: str, *, hidden: bool = False) -> Self:
        """Returns self for chaining"""
        self._definitions.append(PathDefinition(key=key, hidden=hidden))
        return self
```

### Benefits

- **Readability**: Configuration reads like natural language
- **Conciseness**: Multiple operations in one expression
- **Type Safety**: `Self` type ensures correct return type
- **Discoverability**: IDE autocomplete works well

### Usage Example

```python
paths = (PathsBuilder(Path("/home/user"))
    .add("config.app", hidden=False)
    .add("data.cache", hidden=True)
    .add("logs", hidden=False)
    .build())
```

---

## 7. Protocol Pattern (Duck Typing)

### Implementation: os.PathLike Support

The Protocol pattern is used to make ManagedPathTree compatible with os.PathLike.

### Structure

```python
@dataclass(frozen=True, slots=True)
class ManagedPathTree(PathTree):
    def __fspath__(self) -> str:
        """Implement os.PathLike protocol"""
        return str(self.to_path())
```

### Benefits

- **Compatibility**: Works with os and pathlib functions
- **Flexibility**: Can be used anywhere Path is expected
- **No Inheritance**: Uses protocol, not inheritance
- **Type Safety**: Type checkers understand os.PathLike

### Usage Example

```python
managed = ManagedPathTree(base=Path("/home/user"), definitions=[...])

# Works with os functions
os.listdir(managed)  # Uses __fspath__

# Works with pathlib
Path(managed)  # Uses __fspath__

# Works with open
with open(managed / "file.txt") as f:
    content = f.read()
```

---

## 8. Value Object Pattern

### Implementation: PathDefinition

The Value Object pattern is used for PathDefinition to represent immutable configuration.

### Structure

```python
@dataclass(frozen=True, slots=True)
class PathDefinition:
    key: str
    hidden: bool = False
```

### Benefits

- **Immutability**: Cannot be modified after creation
- **Equality**: Compared by value, not identity
- **Hashable**: Can be used in sets and as dict keys
- **Simple**: No behavior, just data

### Usage Example

```python
def1 = PathDefinition(key="config", hidden=False)
def2 = PathDefinition(key="config", hidden=False)

assert def1 == def2  # Equal by value
assert def1 is not def2  # Different objects

# Can be used in sets
definitions = {def1, def2}  # Only one element (equal values)
```

---

## 9. Template Method Pattern

### Implementation: Path Building

The Template Method pattern is used in path building with customizable steps.

### Structure

```python
def _build_path(self, definition: PathDefinition) -> Path:
    """Template method for building paths"""
    segments = self._parse_key(definition.key)  # Step 1
    path = self._base  # Step 2
    for segment in segments[:-1]:  # Step 3
        path = path / segment
    final_segment = segments[-1]  # Step 4
    if definition.hidden:  # Step 5
        final_segment = f".{final_segment}"
    return path / final_segment  # Step 6
```

### Benefits

- **Structure**: Defines algorithm structure
- **Customization**: Steps can be overridden in subclasses
- **Reusability**: Common logic in base implementation
- **Consistency**: Ensures consistent path building

---

## 10. Lazy Initialization Pattern

### Implementation: PathTree Navigation

The Lazy Initialization pattern defers path object creation until needed.

### Structure

```python
class PathTree:
    def __getattr__(self, name: str) -> "PathTree":
        """Lazy creation - only creates when accessed"""
        return PathTree(
            base=self._base,
            segments=self._segments + (name,)
        )
    
    def to_path(self) -> Path:
        """Actual Path created only when needed"""
        path = self._base
        for segment in self._segments:
            path = path / segment
        return path
```

### Benefits

- **Performance**: Avoids unnecessary object creation
- **Memory**: Only creates what's needed
- **Flexibility**: Can navigate without creating paths
- **No I/O**: Navigation doesn't touch filesystem

### Usage Example

```python
paths = PathTree(Path("/home/user"))
# No Path objects created yet

config = paths.config.app.settings
# Still no Path objects - just PathTree instances

# Path created only when needed
final_path = config.to_path()
# Now Path("/home/user/config/app/settings") is created
```

---

## Pattern Interactions

### Builder + Factory Method

```python
builder = PathsBuilder(base)  # Builder pattern
    .add("config")            # Fluent interface
    .build()                  # Factory method
```

### Flyweight + Lazy Initialization

```python
paths = PathTree(base)        # Flyweight
config = paths.config         # Lazy - no Path created
path = config.to_path()       # Initialization - Path created
```

### Composite + Immutable Object

```python
managed = ManagedPathTree(...)  # Composite (extends PathTree)
# Immutable - cannot modify
# But can navigate (PathTree) and create (ManagedPathTree)
```

---

## Anti-Patterns Avoided

### 1. God Object

**Avoided by:** Separating PathTree (navigation), PathsBuilder (building), and ManagedPathTree (creation)

### 2. Mutable State

**Avoided by:** Using frozen dataclasses and immutable collections (tuples)

### 3. Tight Coupling

**Avoided by:** Using protocols (os.PathLike) and type aliases (Segment)

### 4. Premature Optimization

**Avoided by:** Simple, clear implementations with targeted optimizations (`__slots__`)

---

**Next:** [Class Hierarchy](class_hierarchy.md) | [Back to Overview](overview.md)


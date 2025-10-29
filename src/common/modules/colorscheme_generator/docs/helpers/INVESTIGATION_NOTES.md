# Investigation Notes

**Module:** `colorscheme_generator`
**Investigation Started:** 2025-10-18
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Architecture & Structure](#architecture--structure)
2. [Core Abstractions](#core-abstractions)
3. [Type System & Data Models](#type-system--data-models)
4. [Exception Hierarchy](#exception-hierarchy)
5. [Implementation Details](#implementation-details)
6. [Configuration System](#configuration-system)
7. [Template System](#template-system)
8. [Integration & Usage Patterns](#integration--usage-patterns)
9. [Advanced Topics](#advanced-topics)
10. [Code Examples](#code-examples)
11. [Architecture Diagrams](#architecture-diagrams)

---

## Architecture & Structure

### Directory Structure

```
src/dotfiles/modules/colorscheme_generator/
├── config/
│   └── settings.toml              # Configuration file
├── src/colorscheme_generator/
│   ├── __init__.py                # Public API exports
│   ├── cli.py                     # Command-line interface
│   ├── factory.py                 # Factory pattern for backends
│   ├── config/                    # Configuration module
│   │   ├── __init__.py
│   │   ├── enums.py               # Backend, ColorFormat, ColorAlgorithm enums
│   │   ├── defaults.py            # Default configuration values
│   │   ├── config.py              # Pydantic models for configuration
│   │   └── settings.py            # Dynaconf loader + Pydantic validation
│   ├── core/                      # Core abstractions
│   │   ├── __init__.py
│   │   ├── base.py                # ColorSchemeGenerator ABC
│   │   ├── types.py               # Color, ColorScheme, GeneratorConfig
│   │   ├── exceptions.py          # Exception hierarchy
│   │   └── managers/
│   │       ├── __init__.py
│   │       └── output_manager.py  # File writing with Jinja2
│   └── backends/                  # Backend implementations
│       ├── __init__.py
│       ├── pywal.py               # Pywal backend
│       ├── wallust.py             # Wallust backend
│       └── custom.py              # Custom PIL backend
├── templates/                     # Jinja2 templates
│   ├── colors.json.j2
│   ├── colors.sh.j2
│   ├── colors.css.j2
│   └── colors.yaml.j2
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_factory.py
│   └── test_custom_backend.py
├── docs/                          # Documentation
├── pyproject.toml                 # Project metadata and dependencies
├── uv.lock                        # UV lock file
├── Makefile                       # Development commands
└── README.md                      # Project overview
```

### Module Organization

**Package Structure:**
- **Top-level package:** `colorscheme_generator`
- **Subpackages:**
  - `config` - Configuration management (Dynaconf + Pydantic)
  - `core` - Core abstractions and types
  - `core.managers` - OutputManager for file writing
  - `backends` - Backend implementations

**Design Pattern:** Follows the same architecture as `container_manager` module:
- Abstract base class (ABC) pattern
- Factory pattern for backend creation
- Separation of concerns (extraction vs output)
- Dynaconf + Pydantic for configuration

### Public API Surface

**Exported from `__init__.py`:**
```python
__all__ = [
    # Version
    "__version__",
    # Core
    "ColorSchemeGenerator",      # ABC
    "Color",                     # Type
    "ColorScheme",               # Type
    "GeneratorConfig",           # Type
    "OutputManager",             # Manager
    # Config
    "AppConfig",                 # Pydantic model
    "Backend",                   # Enum
    "ColorFormat",               # Enum
    # Factory
    "ColorSchemeGeneratorFactory",
]
```

### Entry Points

1. **CLI Entry Point:** `cli.py` - `main()` function
   - Command-line interface for generating color schemes
   - Supports backend selection, output configuration, format selection

2. **Programmatic Entry Point:** Factory pattern
   ```python
   from colorscheme_generator import ColorSchemeGeneratorFactory
   generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
   scheme = generator.generate(image_path, config)
   ```

3. **Output Writing:**
   ```python
   from colorscheme_generator.core.managers import OutputManager
   manager = OutputManager(settings)
   output_files = manager.write_outputs(scheme, output_dir, formats)
   ```

---

## Core Abstractions

### ColorSchemeGenerator (ABC)

**Location:** `core/base.py`

**Purpose:** Abstract base class that defines the interface for all backend implementations.

**Responsibility:** Extract colors from images and return a `ColorScheme` object. Does NOT write output files.

**Abstract Methods:**
1. `generate(image_path: Path, config: GeneratorConfig) -> ColorScheme`
   - Extract colors from image
   - Returns ColorScheme object
   - Raises: InvalidImageError, ColorExtractionError, BackendNotAvailableError

2. `is_available() -> bool`
   - Check if backend dependencies are installed
   - Returns True if backend can be used

3. `backend_name` (property) -> str
   - Returns backend name (e.g., "pywal", "wallust", "custom")

**Concrete Methods:**
- `ensure_available() -> None` - Convenience method that raises BackendNotAvailableError if not available

**Design Contract:**
- Backends extract colors only
- No file I/O for output (that's OutputManager's job)
- Must validate image before processing
- Must handle backend-specific errors gracefully

### Abstract Methods

**1. generate()**
```python
@abstractmethod
def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
    """Generate color scheme from image."""
    pass
```
- **Input:** Image path + runtime configuration
- **Output:** ColorScheme object with 16 colors + special colors
- **Side effects:** May write to backend-specific cache (e.g., pywal → ~/.cache/wal/)
- **Error handling:** Validates image, checks backend availability

**2. is_available()**
```python
@abstractmethod
def is_available(self) -> bool:
    """Check if backend is available on the system."""
    pass
```
- **Purpose:** Runtime availability check
- **Implementation varies:**
  - Pywal: Check if `pywal` library or `wal` command exists
  - Wallust: Check if `wallust` binary in PATH
  - Custom: Always returns True (PIL is required dependency)

**3. backend_name**
```python
@property
@abstractmethod
def backend_name(self) -> str:
    """Get the backend name."""
    pass
```
- **Returns:** String identifier for backend
- **Used by:** Factory, logging, ColorScheme metadata

### Design Patterns

**1. Abstract Base Class (ABC) Pattern**
- Defines interface contract
- Forces implementations to provide required methods
- Enables polymorphism (swap backends transparently)

**2. Factory Pattern**
- `ColorSchemeGeneratorFactory` creates backend instances
- Supports auto-detection of best available backend
- Centralizes backend instantiation logic

**3. Strategy Pattern**
- Different backends = different strategies for color extraction
- Same interface, different algorithms
- Runtime selection of strategy

**4. Separation of Concerns**
- **Backends:** Color extraction only
- **OutputManager:** File writing only
- **Factory:** Backend creation only
- **Config:** Configuration management only

**5. Template Method Pattern** (in OutputManager)
- `write_outputs()` defines the algorithm
- `_render_template()` and `_write_file()` are the steps
- Jinja2 templates provide format-specific rendering

### Separation of Concerns

**Two-Layer Architecture:**

```
Layer 1: Color Extraction (Backends)
  Input: Image file
  Process: Extract colors using backend-specific algorithm
  Output: ColorScheme object

Layer 2: File Generation (OutputManager)
  Input: ColorScheme object
  Process: Render Jinja2 templates
  Output: Files in various formats
```

**Benefits:**
1. **Modularity:** Can swap backends without changing output logic
2. **Testability:** Can test extraction and output independently
3. **Flexibility:** Can add new backends or formats without affecting the other layer
4. **Clarity:** Each component has a single, well-defined responsibility

**Contrast with Monolithic Approach:**
- ❌ Pywal writes its own files → we can't control format/location
- ✅ We extract colors from pywal, then write our own files → full control

**Backend Independence:**
- Pywal: Writes to ~/.cache/wal/ (we read from there, then write our own files)
- Wallust: Outputs JSON to stdout (we parse it, then write our own files)
- Custom: Pure Python (we control everything, then write our own files)

---

## Type System & Data Models

### Enums

*To be documented in Phase 3*

### Pydantic Models

*To be documented in Phase 3*

### Color Type

*To be documented in Phase 3*

### ColorScheme Type

*To be documented in Phase 3*

### Configuration Models

*To be documented in Phase 3*

---

## Exception Hierarchy

### Exception Classes

*To be documented in Phase 4*

### Error Contexts

*To be documented in Phase 4*

### Error Handling Patterns

*To be documented in Phase 4*

---

## Implementation Details

### PywalGenerator

*To be documented in Phase 5*

### WallustGenerator

*To be documented in Phase 5*

### CustomGenerator

*To be documented in Phase 5*

### OutputManager

*To be documented in Phase 5*

### Factory

*To be documented in Phase 5*

### Utilities

*To be documented in Phase 5*

---

## Configuration System

### Settings Class

*To be documented in Phase 6*

### settings.toml Structure

*To be documented in Phase 6*

### Configuration Hierarchy

*To be documented in Phase 6*

### Backend Configuration

*To be documented in Phase 6*

---

## Template System

### Jinja2 Templates

*To be documented in Phase 7*

### Template Variables

*To be documented in Phase 7*

### Rendering Process

*To be documented in Phase 7*

### Custom Templates

*To be documented in Phase 7*

---

## Integration & Usage Patterns

### Common Usage Patterns

*To be documented in Phase 8*

### Integration with Dotfiles

*To be documented in Phase 8*

### Workflows

*To be documented in Phase 8*

### CLI Usage

*To be documented in Phase 8*

### Best Practices

*To be documented in Phase 8*

---

## Advanced Topics

### Security Considerations

*To be documented in Phase 9*

### Performance Considerations

*To be documented in Phase 9*

### Extensibility Points

*To be documented in Phase 9*

### Testing Strategy

*To be documented in Phase 9*

### Troubleshooting

*To be documented in Phase 9*

---

## Code Examples

*Examples will be added throughout the investigation*

---

## Architecture Diagrams

*Diagrams will be added throughout the investigation*

---

**Note:** This document will be populated as the investigation progresses. Each section will contain detailed findings, code examples, and insights discovered during the investigation.


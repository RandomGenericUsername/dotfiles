# Architecture Overview

**Module:** `colorscheme_generator`  
**Version:** 0.1.0  
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Component Overview](#component-overview)
3. [Data Flow](#data-flow)
4. [Design Principles](#design-principles)
5. [Module Structure](#module-structure)
6. [Dependencies](#dependencies)

---

## High-Level Architecture

The `colorscheme_generator` module follows a **two-layer architecture** that separates color extraction from file generation:

```
┌─────────────────────────────────────────────────────────────┐
│                     User / CLI / API                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ColorSchemeGeneratorFactory                 │
│              (Creates backend instances)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: BACKENDS                         │
│              (Color Extraction from Images)                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Pywal      │  │   Wallust    │  │   Custom     │      │
│  │  Generator   │  │  Generator   │  │  Generator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                            ▼                                 │
│                    ColorScheme Object                        │
│         (background, foreground, cursor, 16 colors)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LAYER 2: OUTPUT                            │
│              (File Generation from ColorScheme)              │
├─────────────────────────────────────────────────────────────┤
│                    OutputManager                             │
│              (Jinja2 Template Rendering)                     │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐             │
│         ▼                  ▼                  ▼             │
│    colors.json        colors.css         colors.sh          │
│    colors.yaml        colors.toml                           │
└─────────────────────────────────────────────────────────────┘
```

### Key Characteristics

1. **Separation of Concerns**
   - Layer 1 (Backends): Extract colors from images
   - Layer 2 (OutputManager): Write colors to files
   - No coupling between layers

2. **Backend Independence**
   - Each backend uses different tools/algorithms
   - All return the same `ColorScheme` type
   - OutputManager doesn't know which backend was used

3. **Format Independence**
   - Backends don't know about output formats
   - OutputManager handles all format generation
   - Easy to add new formats without touching backends

---

## Component Overview

### Core Components

#### 1. ColorSchemeGenerator (ABC)
**Location:** `core/base.py`  
**Purpose:** Abstract base class for all backends  
**Responsibility:** Define interface for color extraction

**Key Methods:**
- `generate(image_path, config) -> ColorScheme` - Extract colors
- `is_available() -> bool` - Check if backend is available
- `backend_name` - Get backend identifier

#### 2. Backend Implementations
**Location:** `backends/`  
**Purpose:** Concrete implementations of ColorSchemeGenerator

**Backends:**
- **PywalGenerator** - Uses pywal (Python/CLI) for color extraction
- **WallustGenerator** - Uses wallust (Rust binary) for color extraction
- **CustomGenerator** - Uses PIL/scikit-learn for color extraction

#### 3. OutputManager
**Location:** `core/managers/output_manager.py`  
**Purpose:** Write ColorScheme objects to files  
**Responsibility:** Template rendering and file I/O

**Key Methods:**
- `write_outputs(scheme, output_dir, formats) -> dict` - Write all formats
- `_render_template(scheme, format) -> str` - Render single template
- `_write_file(path, content)` - Write to disk

#### 4. ColorSchemeGeneratorFactory
**Location:** `factory.py`  
**Purpose:** Create backend instances  
**Responsibility:** Backend instantiation and auto-detection

**Key Methods:**
- `create(backend, settings) -> ColorSchemeGenerator` - Create specific backend
- `create_auto(settings) -> ColorSchemeGenerator` - Auto-detect best backend
- `list_available(settings) -> list[str]` - List available backends

#### 5. Configuration System
**Location:** `config/`  
**Purpose:** Manage settings and configuration  
**Components:**
- `Settings` - Dynaconf loader
- `AppConfig` - Pydantic validation model
- `GeneratorConfig` - Runtime configuration
- Enums: `Backend`, `ColorFormat`, `ColorAlgorithm`

### Supporting Components

#### 6. Type System
**Location:** `core/types.py`  
**Types:**
- `Color` - Single color (hex, RGB, HSL)
- `ColorScheme` - Complete color scheme (background, foreground, cursor, 16 colors)
- `GeneratorConfig` - Runtime configuration for generation

#### 7. Exception Hierarchy
**Location:** `core/exceptions.py`  
**Exceptions:**
- `ColorSchemeGeneratorError` - Base exception
- `BackendNotAvailableError` - Backend not installed
- `ColorExtractionError` - Color extraction failed
- `TemplateRenderError` - Template rendering failed
- `OutputWriteError` - File writing failed
- `InvalidImageError` - Invalid image file

#### 8. Template System
**Location:** `templates/`  
**Purpose:** Jinja2 templates for output formats  
**Templates:**
- `colors.json.j2` - JSON format
- `colors.sh.j2` - Shell script format
- `colors.css.j2` - CSS variables format
- `colors.yaml.j2` - YAML format

---

## Data Flow

### Complete Workflow

```
1. User Input
   ├─ Image path
   ├─ Backend selection (or auto)
   ├─ Output directory
   └─ Output formats

2. Configuration
   ├─ Load settings.toml (Dynaconf)
   ├─ Validate with Pydantic (AppConfig)
   ├─ Merge with runtime overrides (GeneratorConfig)
   └─ Resolve environment variables

3. Backend Creation
   ├─ Factory.create() or Factory.create_auto()
   ├─ Instantiate backend with settings
   └─ Check availability (is_available())

4. Color Extraction (Layer 1)
   ├─ Validate image file
   ├─ Run backend-specific extraction
   │  ├─ Pywal: Run pywal, read ~/.cache/wal/colors.json
   │  ├─ Wallust: Run wallust, parse JSON from stdout
   │  └─ Custom: Use PIL + K-means/median-cut/octree
   └─ Return ColorScheme object

5. File Generation (Layer 2)
   ├─ OutputManager.write_outputs()
   ├─ For each format:
   │  ├─ Load Jinja2 template
   │  ├─ Render with ColorScheme data
   │  └─ Write to file
   └─ Return dict of output files

6. Result
   └─ Dictionary mapping format → file path
```

### Data Transformations

```
Image File (PNG/JPG)
    ↓ [Backend]
Raw Colors (backend-specific format)
    ↓ [Backend parsing]
ColorScheme Object (standardized)
    ↓ [OutputManager + Jinja2]
Output Files (JSON/CSS/Shell/YAML)
```

---

## Design Principles

### 1. Single Responsibility Principle

Each component has one clear responsibility:
- **Backends:** Extract colors from images
- **OutputManager:** Write colors to files
- **Factory:** Create backend instances
- **Config:** Manage settings
- **Types:** Define data structures

### 2. Open/Closed Principle

- **Open for extension:** Easy to add new backends or formats
- **Closed for modification:** Adding new backends doesn't require changing existing code

Example: Adding a new backend
```python
# Just implement the interface
class NewBackend(ColorSchemeGenerator):
    def generate(self, image_path, config):
        # Your implementation
        return ColorScheme(...)
    
    def is_available(self):
        return True
    
    @property
    def backend_name(self):
        return "new_backend"

# Register in factory
# No changes to OutputManager or other backends needed!
```

### 3. Dependency Inversion Principle

- High-level modules (Factory, CLI) depend on abstractions (ColorSchemeGenerator)
- Low-level modules (PywalGenerator, etc.) implement abstractions
- Both depend on the abstraction, not on each other

### 4. Interface Segregation Principle

- ColorSchemeGenerator interface is minimal (3 methods)
- OutputManager has its own focused interface
- No client is forced to depend on methods it doesn't use

### 5. Liskov Substitution Principle

- Any ColorSchemeGenerator implementation can be used interchangeably
- Factory.create() returns ColorSchemeGenerator
- Client code works with any backend without modification

---

## Module Structure

```
colorscheme_generator/
├── __init__.py              # Public API exports
├── cli.py                   # Command-line interface
├── factory.py               # Factory pattern
├── config/                  # Configuration
│   ├── __init__.py
│   ├── enums.py            # Backend, ColorFormat, ColorAlgorithm
│   ├── defaults.py         # Default values
│   ├── config.py           # Pydantic models
│   └── settings.py         # Dynaconf loader
├── core/                    # Core abstractions
│   ├── __init__.py
│   ├── base.py             # ColorSchemeGenerator ABC
│   ├── types.py            # Color, ColorScheme, GeneratorConfig
│   ├── exceptions.py       # Exception hierarchy
│   └── managers/
│       ├── __init__.py
│       └── output_manager.py  # File writing
└── backends/                # Backend implementations
    ├── __init__.py
    ├── pywal.py            # Pywal backend
    ├── wallust.py          # Wallust backend
    └── custom.py           # Custom PIL backend
```

---

## Dependencies

### Core Dependencies

```toml
dependencies = [
    "pydantic>=2.11.9",      # Type validation
    "pillow>=10.0.0",        # Image processing (custom backend)
    "jinja2>=3.1.6",         # Template rendering
    "dynaconf>=3.2.0",       # Configuration management
    "numpy>=1.24.0",         # Array operations (custom backend)
    "scikit-learn>=1.3.0",   # K-means clustering (custom backend)
]
```

### Optional Dependencies

```toml
[project.optional-dependencies]
pywal = ["pywal>=3.3.0"]     # Pywal backend
dev = ["pytest", "pytest-cov", "ruff", "mypy"]
```

### External Tools (Optional)

- **pywal** - Python package or CLI tool
- **wallust** - Rust binary (install via cargo)

---

## Next Steps

- **[Design Patterns](design_patterns.md)** - Detailed pattern documentation
- **[Component Relationships](component_relationships.md)** - How components interact
- **[API Reference](../api/)** - Detailed API documentation


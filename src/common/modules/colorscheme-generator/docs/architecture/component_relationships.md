# Component Relationships

**Module:** `colorscheme_generator`
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Component Diagram](#component-diagram)
2. [Dependency Graph](#dependency-graph)
3. [Interaction Patterns](#interaction-patterns)
4. [Data Flow](#data-flow)
5. [Communication Protocols](#communication-protocols)

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI / User Code                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ├──────────────────┬──────────────────┐
                         ▼                  ▼                  ▼
              ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
              │     Factory      │  │   Settings   │  │GeneratorConfig│
              └────────┬─────────┘  └──────┬───────┘  └──────┬───────┘
                       │                   │                  │
                       │                   └──────────────────┘
                       │                            │
                       ▼                            ▼
              ┌──────────────────┐        ┌──────────────────┐
              │ColorSchemeGenerator│◄──────│   AppConfig     │
              │      (ABC)       │        │  (Pydantic)     │
              └────────┬─────────┘        └─────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│   Pywal    │  │  Wallust   │  │   Custom   │
│ Generator  │  │ Generator  │  │ Generator  │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │               │               │
      └───────────────┴───────────────┘
                      │
                      ▼
              ┌──────────────────┐
              │  ColorScheme     │
              │    (Type)        │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  OutputManager   │
              └────────┬─────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    colors.json   colors.css    colors.sh
    colors.yaml   colors.toml
```

---

## Dependency Graph

### Direct Dependencies

```
CLI
 ├─→ Factory
 ├─→ Settings
 ├─→ GeneratorConfig
 ├─→ OutputManager
 └─→ Exceptions

Factory
 ├─→ ColorSchemeGenerator (ABC)
 ├─→ PywalGenerator
 ├─→ WallustGenerator
 ├─→ CustomGenerator
 └─→ AppConfig

ColorSchemeGenerator (ABC)
 ├─→ ColorScheme
 ├─→ GeneratorConfig
 └─→ Exceptions

PywalGenerator / WallustGenerator / CustomGenerator
 ├─→ ColorSchemeGenerator (ABC)
 ├─→ AppConfig
 ├─→ ColorScheme
 ├─→ Color
 └─→ Exceptions

OutputManager
 ├─→ AppConfig
 ├─→ ColorScheme
 ├─→ ColorFormat
 ├─→ Jinja2
 └─→ Exceptions

GeneratorConfig
 ├─→ AppConfig
 ├─→ Backend
 └─→ ColorFormat

Settings
 ├─→ Dynaconf
 ├─→ AppConfig
 └─→ Pydantic

AppConfig
 ├─→ Pydantic
 └─→ Enums
```

### Dependency Layers

```
Layer 1 (Foundation):
  - Enums (Backend, ColorFormat, ColorAlgorithm)
  - Exceptions
  - External: Pydantic, Dynaconf, Jinja2

Layer 2 (Types):
  - Color
  - ColorScheme
  - AppConfig
  - GeneratorConfig

Layer 3 (Core Abstractions):
  - ColorSchemeGenerator (ABC)
  - Settings

Layer 4 (Implementations):
  - PywalGenerator
  - WallustGenerator
  - CustomGenerator
  - OutputManager

Layer 5 (Orchestration):
  - Factory
  - CLI
```

---

## Interaction Patterns

### Pattern 1: Color Extraction

```
User Code
    │
    ├─→ Factory.create(Backend.PYWAL, settings)
    │       │
    │       └─→ PywalGenerator(settings)
    │               │
    │               └─→ stores settings
    │
    ├─→ generator.generate(image_path, config)
    │       │
    │       ├─→ validate image
    │       ├─→ run pywal
    │       ├─→ read colors.json
    │       └─→ return ColorScheme
    │
    └─→ receives ColorScheme
```

### Pattern 2: File Generation

```
User Code
    │
    ├─→ OutputManager(settings)
    │       │
    │       └─→ setup Jinja2 environment
    │
    ├─→ manager.write_outputs(scheme, dir, formats)
    │       │
    │       ├─→ for each format:
    │       │   ├─→ load template
    │       │   ├─→ render with scheme data
    │       │   └─→ write to file
    │       │
    │       └─→ return {format: path}
    │
    └─→ receives output files dict
```

### Pattern 3: Auto-Detection

```
User Code
    │
    ├─→ Factory.create_auto(settings)
    │       │
    │       ├─→ try WallustGenerator
    │       │   └─→ is_available()? → No
    │       │
    │       ├─→ try PywalGenerator
    │       │   └─→ is_available()? → Yes!
    │       │
    │       └─→ return PywalGenerator
    │
    └─→ receives best available backend
```

### Pattern 4: Configuration Hierarchy

```
User Code
    │
    ├─→ Settings.get()
    │       │
    │       ├─→ Dynaconf loads settings.toml
    │       ├─→ resolve environment variables
    │       ├─→ convert to lowercase
    │       └─→ validate with Pydantic → AppConfig
    │
    ├─→ GeneratorConfig.from_settings(settings, **overrides)
    │       │
    │       ├─→ merge settings with overrides
    │       └─→ return GeneratorConfig
    │
    └─→ receives final configuration
```

---

## Data Flow

### Complete Workflow

```
1. Initialization
   ┌─────────────┐
   │ User Code   │
   └──────┬──────┘
          │
          ├─→ Settings.get() → AppConfig
          │
          └─→ GeneratorConfig.from_settings() → GeneratorConfig

2. Backend Creation
   ┌─────────────┐
   │ User Code   │
   └──────┬──────┘
          │
          └─→ Factory.create() → ColorSchemeGenerator

3. Color Extraction
   ┌─────────────┐
   │ User Code   │
   └──────┬──────┘
          │
          └─→ generator.generate()
                  │
                  ├─→ validate image
                  ├─→ extract colors (backend-specific)
                  └─→ ColorScheme

4. File Generation
   ┌─────────────┐
   │ User Code   │
   └──────┬──────┘
          │
          └─→ OutputManager.write_outputs()
                  │
                  ├─→ render templates
                  ├─→ write files
                  └─→ {format: path}

5. Result
   ┌─────────────┐
   │ User Code   │
   └──────┬──────┘
          │
          └─→ receives output files
```

### Data Transformations

```
settings.toml (TOML)
    ↓ [Dynaconf]
dict
    ↓ [Pydantic]
AppConfig
    ↓ [GeneratorConfig.from_settings]
GeneratorConfig
    ↓ [Factory.create]
ColorSchemeGenerator
    ↓ [generator.generate]
ColorScheme
    ↓ [OutputManager.write_outputs]
Files (JSON/CSS/Shell/YAML)
```

---

## Communication Protocols

### Backend → ColorScheme

**Protocol:** Return value
**Data:** ColorScheme object
**Contract:**
- Must have background, foreground, cursor colors
- Must have exactly 16 terminal colors
- Must include metadata (source_image, backend, generated_at)

```python
# Backend produces
ColorScheme(
    background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
    foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
    cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
    colors=[...],  # 16 colors
    source_image="/path/to/image.png",
    backend="pywal",
    generated_at=datetime.now()
)
```

### ColorScheme → OutputManager

**Protocol:** Method parameter
**Data:** ColorScheme object
**Contract:**
- ColorScheme must be valid (Pydantic validated)
- OutputManager doesn't modify ColorScheme
- OutputManager only reads data for template rendering

```python
# OutputManager consumes
def write_outputs(self, scheme: ColorScheme, ...):
    context = {
        "background": scheme.background,
        "foreground": scheme.foreground,
        "cursor": scheme.cursor,
        "colors": scheme.colors,
        ...
    }
```

### Settings → Components

**Protocol:** Constructor injection
**Data:** AppConfig object
**Contract:**
- Settings injected at construction time
- Components store reference to settings
- Settings are immutable during component lifetime

```python
# Components receive settings
class PywalGenerator:
    def __init__(self, settings: AppConfig):
        self.settings = settings
        # Extract needed config
        self.cache_dir = settings.backends.pywal.cache_dir
```

### Factory → Backends

**Protocol:** Factory method
**Data:** Backend enum + AppConfig
**Contract:**
- Factory creates backend instance
- Factory passes settings to backend
- Backend is ready to use after creation

```python
# Factory creates backend
def create(backend: Backend, settings: AppConfig) -> ColorSchemeGenerator:
    if backend == Backend.PYWAL:
        return PywalGenerator(settings)  # Inject settings
```

---

## Component Coupling

### Loose Coupling

✅ **Backends ↔ OutputManager**
- No direct dependency
- Communicate through ColorScheme interface
- Can be used independently

✅ **Factory ↔ Backends**
- Factory depends on backend classes
- Backends don't know about Factory
- One-way dependency

✅ **CLI ↔ Core**
- CLI depends on core components
- Core doesn't know about CLI
- Clean separation

### Tight Coupling (Intentional)

⚠️ **Backends → AppConfig**
- Backends need configuration
- Acceptable: Configuration is stable
- Mitigated: Dependency injection

⚠️ **OutputManager → Jinja2**
- OutputManager needs template engine
- Acceptable: Jinja2 is standard
- Mitigated: Could abstract if needed

⚠️ **Settings → Dynaconf + Pydantic**
- Settings needs both libraries
- Acceptable: Configuration pattern
- Mitigated: Isolated in config module

---

## Extension Points

### Adding a New Backend

```python
# 1. Implement interface
class NewBackend(ColorSchemeGenerator):
    def __init__(self, settings: AppConfig):
        self.settings = settings

    def generate(self, image_path, config):
        # Your implementation
        return ColorScheme(...)

    def is_available(self):
        return True

    @property
    def backend_name(self):
        return "new_backend"

# 2. Register in factory
# factory.py
def create(backend: Backend, settings: AppConfig):
    if backend == Backend.NEW:
        return NewBackend(settings)

# 3. Add to enum
# enums.py
class Backend(str, Enum):
    NEW = "new_backend"

# No changes needed to:
# - OutputManager
# - ColorScheme
# - Other backends
# - CLI (except to add option)
```

### Adding a New Output Format

```python
# 1. Create template
# templates/colors.newformat.j2
{{ background.hex }}
{{ foreground.hex }}

# 2. Add to enum
# enums.py
class ColorFormat(str, Enum):
    NEWFORMAT = "newformat"

# No changes needed to:
# - OutputManager (automatically picks up template)
# - Backends
# - ColorScheme
# - CLI (except to add option)
```

---

## Next Steps

- **[API Reference](../api/)** - Detailed API documentation
- **[Usage Patterns](../guides/usage_patterns.md)** - Common usage patterns
- **[Examples](../reference/examples.md)** - Comprehensive examples

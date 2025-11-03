# Design Patterns

**Module:** `colorscheme_generator`
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Abstract Factory Pattern](#abstract-factory-pattern)
2. [Strategy Pattern](#strategy-pattern)
3. [Template Method Pattern](#template-method-pattern)
4. [Dependency Injection](#dependency-injection)
5. [Separation of Concerns](#separation-of-concerns)
6. [Configuration Pattern](#configuration-pattern)

---

## Abstract Factory Pattern

### Overview

The `ColorSchemeGeneratorFactory` implements the Abstract Factory pattern to create backend instances without exposing instantiation logic to clients.

### Implementation

```python
class ColorSchemeGeneratorFactory:
    """Factory for creating ColorSchemeGenerator instances."""

    @staticmethod
    def create(backend: Backend, settings: AppConfig) -> ColorSchemeGenerator:
        """Create a specific backend instance."""
        if backend == Backend.PYWAL:
            return PywalGenerator(settings)
        elif backend == Backend.WALLUST:
            return WallustGenerator(settings)
        elif backend == Backend.CUSTOM:
            return CustomGenerator(settings)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    @staticmethod
    def create_auto(settings: AppConfig) -> ColorSchemeGenerator:
        """Automatically detect and create best available backend."""
        backends_to_try = [
            (Backend.WALLUST, WallustGenerator),
            (Backend.PYWAL, PywalGenerator),
            (Backend.CUSTOM, CustomGenerator),
        ]

        for backend_type, backend_class in backends_to_try:
            generator = backend_class(settings)
            if generator.is_available():
                return generator

        raise BackendNotAvailableError("none", "No backends available")
```

### Benefits

1. **Encapsulation** - Client doesn't need to know about concrete classes
2. **Flexibility** - Easy to add new backends
3. **Auto-detection** - Can automatically select best available backend
4. **Consistency** - All backends created through same interface

### Usage

```python
# Create specific backend
generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)

# Auto-detect best backend
generator = ColorSchemeGeneratorFactory.create_auto(settings)

# List available backends
available = ColorSchemeGeneratorFactory.list_available(settings)
```

---

## Strategy Pattern

### Overview

Different backends represent different strategies for color extraction. All implement the same interface (`ColorSchemeGenerator`), allowing runtime selection of algorithm.

### Implementation

```python
# Strategy interface
class ColorSchemeGenerator(ABC):
    @abstractmethod
    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
        pass

# Concrete strategies
class PywalGenerator(ColorSchemeGenerator):
    def generate(self, image_path, config):
        # Pywal strategy: Use pywal library/CLI
        ...

class WallustGenerator(ColorSchemeGenerator):
    def generate(self, image_path, config):
        # Wallust strategy: Use wallust binary
        ...

class CustomGenerator(ColorSchemeGenerator):
    def generate(self, image_path, config):
        # Custom strategy: Use PIL + K-means
        ...
```

### Benefits

1. **Interchangeability** - Swap backends without changing client code
2. **Extensibility** - Add new strategies without modifying existing ones
3. **Runtime Selection** - Choose strategy at runtime based on availability
4. **Testability** - Easy to test each strategy independently

### Usage

```python
# Client code works with any strategy
def process_image(image_path: Path, generator: ColorSchemeGenerator):
    scheme = generator.generate(image_path, config)
    return scheme

# Can use any backend
process_image(image_path, PywalGenerator(settings))
process_image(image_path, WallustGenerator(settings))
process_image(image_path, CustomGenerator(settings))
```

---

## Template Method Pattern

### Overview

The `OutputManager` uses the Template Method pattern to define the algorithm for writing output files, with specific steps that can vary.

### Implementation

```python
class OutputManager:
    def write_outputs(self, scheme, output_dir, formats):
        """Template method - defines the algorithm."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_files = {}

        for fmt in formats:
            # Step 1: Render template (varies by format)
            content = self._render_template(scheme, fmt)

            # Step 2: Write to file (same for all formats)
            output_path = output_dir / f"colors.{fmt.value}"
            self._write_file(output_path, content)

            output_files[fmt.value] = output_path

        return output_files

    def _render_template(self, scheme, fmt):
        """Primitive operation - varies by format."""
        template = self.template_env.get_template(f"colors.{fmt.value}.j2")
        return template.render(...)

    def _write_file(self, path, content):
        """Primitive operation - same for all formats."""
        path.write_text(content)
```

### Benefits

1. **Code Reuse** - Common algorithm defined once
2. **Consistency** - All formats follow same process
3. **Flexibility** - Easy to customize specific steps
4. **Maintainability** - Changes to algorithm affect all formats

---

## Dependency Injection

### Overview

Dependencies (like `AppConfig`) are injected into components rather than created internally, enabling flexibility and testability.

### Implementation

```python
# Dependencies injected via constructor
class PywalGenerator(ColorSchemeGenerator):
    def __init__(self, settings: AppConfig):
        self.settings = settings  # Injected dependency
        self.cache_dir = settings.backends.pywal.cache_dir
        self.use_library = settings.backends.pywal.use_library

class OutputManager:
    def __init__(self, settings: AppConfig):
        self.settings = settings  # Injected dependency
        template_dir = settings.templates.directory
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
```

### Benefits

1. **Testability** - Easy to inject mock dependencies for testing
2. **Flexibility** - Can use different configurations
3. **Decoupling** - Components don't create their own dependencies
4. **Clarity** - Dependencies are explicit in constructor

### Usage

```python
# Production
settings = Settings.get()
generator = PywalGenerator(settings)

# Testing
mock_settings = MockAppConfig(...)
generator = PywalGenerator(mock_settings)
```

---

## Separation of Concerns

### Overview

The module strictly separates color extraction (backends) from file generation (OutputManager), ensuring each component has a single, well-defined responsibility.

### Architecture

```
┌─────────────────────────────────────┐
│         LAYER 1: BACKENDS           │
│    (Color Extraction Only)          │
│                                     │
│  Responsibility:                    │
│  - Extract colors from images       │
│  - Return ColorScheme object        │
│  - NO file writing                  │
└─────────────────────────────────────┘
              │
              ▼ ColorScheme
┌─────────────────────────────────────┐
│      LAYER 2: OUTPUT MANAGER        │
│    (File Generation Only)           │
│                                     │
│  Responsibility:                    │
│  - Render Jinja2 templates          │
│  - Write files to disk              │
│  - NO color extraction              │
└─────────────────────────────────────┘
```

### Benefits

1. **Modularity** - Can change one layer without affecting the other
2. **Testability** - Test extraction and output independently
3. **Reusability** - Can use backends without OutputManager, or vice versa
4. **Clarity** - Each component has clear, focused responsibility

### Example

```python
# Backend only extracts colors
generator = PywalGenerator(settings)
scheme = generator.generate(image_path, config)  # Returns ColorScheme

# OutputManager only writes files
manager = OutputManager(settings)
files = manager.write_outputs(scheme, output_dir, formats)  # Writes files

# They don't know about each other!
```

---

## Configuration Pattern

### Overview

The module uses a hierarchical configuration pattern with Dynaconf + Pydantic, following the same approach as the container_manager module.

### Layers

```
1. Defaults (defaults.py)
   ↓
2. Settings File (settings.toml) - loaded by Dynaconf
   ↓
3. Pydantic Validation (AppConfig)
   ↓
4. Runtime Overrides (GeneratorConfig)
   ↓
5. Final Configuration
```

### Implementation

```python
# Layer 1: Defaults
# defaults.py
output_directory = Path.home() / ".cache/colorscheme"
default_backend = "pywal"

# Layer 2: Settings File
# settings.toml
[output]
directory = "$HOME/.cache/colorscheme"

# Layer 3: Pydantic Validation
class AppConfig(BaseModel):
    output: OutputSettings
    generation: GenerationSettings
    backends: BackendSettings

# Layer 4: Runtime Overrides
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.WALLUST,  # Override
    output_dir=Path("/tmp/colors")  # Override
)
```

### Benefits

1. **Flexibility** - Multiple levels of configuration
2. **Type Safety** - Pydantic validates all settings
3. **Environment Variables** - Dynaconf resolves $HOME, etc.
4. **Defaults** - Sensible defaults for all settings
5. **Overrides** - Easy to override at runtime

---

## Pattern Relationships

### How Patterns Work Together

```
Factory Pattern
    ↓ creates
Strategy Pattern (Backends)
    ↓ uses
Dependency Injection (Settings)
    ↓ configured by
Configuration Pattern
    ↓ produces
ColorScheme
    ↓ consumed by
Template Method Pattern (OutputManager)
    ↓ uses
Dependency Injection (Settings)
```

### Example Workflow

```python
# 1. Configuration Pattern
settings = Settings.get()  # Dynaconf + Pydantic

# 2. Factory Pattern
generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)

# 3. Strategy Pattern + Dependency Injection
scheme = generator.generate(image_path, config)  # Uses injected settings

# 4. Separation of Concerns
# (Backend done, now OutputManager)

# 5. Template Method Pattern + Dependency Injection
manager = OutputManager(settings)  # Injected settings
files = manager.write_outputs(scheme, output_dir, formats)
```

---

## Anti-Patterns Avoided

### 1. God Object
❌ **Avoided:** No single class does everything
✅ **Instead:** Separate classes for extraction, output, config, factory

### 2. Tight Coupling
❌ **Avoided:** Backends don't know about OutputManager
✅ **Instead:** Communicate through ColorScheme interface

### 3. Hard-Coded Dependencies
❌ **Avoided:** No hard-coded paths or settings
✅ **Instead:** Dependency injection + configuration

### 4. Monolithic Design
❌ **Avoided:** Not a single large class
✅ **Instead:** Multiple focused components

### 5. Leaky Abstractions
❌ **Avoided:** Backend details don't leak to clients
✅ **Instead:** Clean ABC interface hides implementation

---

## Next Steps

- **[Component Relationships](component_relationships.md)** - How components interact
- **[API Reference](../api/)** - Detailed API documentation
- **[Usage Patterns](../guides/usage_patterns.md)** - Common usage patterns

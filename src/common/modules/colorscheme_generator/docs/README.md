# Colorscheme Generator Documentation

**Version:** 0.1.0
**Status:** In Development
**Last Updated:** 2025-10-18

---

## Overview

The `colorscheme_generator` module is a flexible, extensible system for extracting color schemes from images using multiple backends (pywal, wallust, custom) and writing them to various output formats (JSON, Shell, CSS, YAML, TOML).

### Key Features

- 🎨 **Multiple Backends** - Pywal, Wallust, or custom Python implementation
- 📁 **Multiple Formats** - JSON, Shell, CSS, YAML, TOML
- ⚙️ **Flexible Configuration** - Settings file + runtime overrides
- 🔧 **Clean Architecture** - Separation between color extraction and file generation
- 🚀 **Type Safe** - Full Pydantic validation
- 📦 **Isolated Project** - Independent UV project with own dependencies

### Architecture at a Glance

```
Image → Backend (extract colors) → ColorScheme → OutputManager (write files) → Files
```

**Two-layer design:**
1. **Backends** - Extract colors from images, return `ColorScheme` object
2. **OutputManager** - Write `ColorScheme` to files using Jinja2 templates

This separation means:
- Backends don't care about output formats or locations
- OutputManager doesn't care how colors were extracted
- You can swap backends without changing output logic

---

## Documentation Structure

This documentation is organized into five main sections:

### 📊 [Diagrams](diagrams/)
**50+ comprehensive Mermaid diagrams** covering all aspects of the module.

- **[All Diagrams Index](diagrams/README.md)** - Complete diagram catalog
- **[High-Level Architecture](diagrams/01-high-level-architecture.md)** - System overview
- **[Data Flow](diagrams/02-data-flow.md)** - Processing pipeline
- **[Class Diagram](diagrams/03-class-diagram.md)** - Object structure
- **[Sequence Diagram](diagrams/04-sequence-diagram.md)** - Component interactions
- **[Backend Comparison](diagrams/05-backend-comparison.md)** - Backend differences
- **[Configuration System](diagrams/06-configuration-system.md)** - Config hierarchy
- **[Template System](diagrams/07-template-system.md)** - Template rendering
- **[Exception Hierarchy](diagrams/08-exception-hierarchy.md)** - Error handling
- **[Integration Patterns](diagrams/09-integration-patterns.md)** - System integration
- **[State Machine](diagrams/10-state-machine.md)** - State transitions

### 📐 [Architecture](architecture/)
Understand the design and structure of the module.

- **[Overview](architecture/overview.md)** - High-level architecture and design principles
- **[Design Patterns](architecture/design_patterns.md)** - Patterns used throughout the module
- **[Component Relationships](architecture/component_relationships.md)** - How components interact

### 📚 [API Reference](api/)
Detailed documentation of all classes, functions, and types.

- **[Core](api/core.md)** - Core abstractions (ColorSchemeGenerator, Color, ColorScheme)
- **[Backends](api/backends.md)** - Backend implementations (Pywal, Wallust, Custom)
- **[Managers](api/managers.md)** - OutputManager for file writing
- **[Configuration](api/configuration.md)** - Configuration system (Settings, AppConfig)
- **[Exceptions](api/exceptions.md)** - Exception hierarchy and error handling

### 📖 [Guides](guides/)
Practical guides for using the module.

- **[Getting Started](guides/getting_started.md)** - Quick start guide
- **[Usage Patterns](guides/usage_patterns.md)** - Common usage patterns and workflows
- **[Integration](guides/integration.md)** - Integrating with other modules
- **[Templates](guides/templates.md)** - Working with Jinja2 templates

### 🔍 [Reference](reference/)
Additional reference material.

- **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions
- **[Examples](reference/examples.md)** - Comprehensive code examples
- **[Advanced Topics](reference/advanced_topics.md)** - Security, performance, extensibility

---

## Quick Start

### Installation

```bash
cd src/dotfiles/modules/colorscheme_generator

# Create virtual environment and install
uv venv
uv sync
uv pip install -e .

# Optional: install pywal backend
uv pip install -e ".[pywal]"

# Development dependencies
uv pip install -e ".[dev]"
```

### Basic Usage

```python
from pathlib import Path
from colorscheme_generator import (
    ColorSchemeGeneratorFactory,
    OutputManager,
    Settings,
    GeneratorConfig,
    Backend,
    ColorFormat,
)

# Load settings
settings = Settings.get()

# Create config
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.PYWAL,
    output_dir=Path("~/.cache/colorscheme"),
    formats=[ColorFormat.JSON, ColorFormat.CSS]
)

# Extract colors
generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
scheme = generator.generate(Path("~/wallpapers/mountain.png"), config)

# Write files
output_manager = OutputManager(settings)
output_files = output_manager.write_outputs(scheme, config.output_dir, config.formats)

print(f"Generated: {output_files}")
```

### CLI Usage

```bash
# Generate with auto-detected backend
colorscheme-gen wallpaper.png

# Use specific backend
colorscheme-gen wallpaper.png --backend pywal

# Custom output directory and formats
colorscheme-gen wallpaper.png -o ~/.config/colors -f json css

# List available backends
colorscheme-gen --list-backends
```

---

## Design Principles

### 1. Separation of Concerns

- **Backends** extract colors → return `ColorScheme` object
- **OutputManager** writes `ColorScheme` → files
- Clean separation, no coupling

### 2. Backend Independence

- Pywal writes to `~/.cache/wal/` (we just read from there)
- Wallust outputs JSON to stdout (we parse it)
- Custom uses PIL (full control)
- OutputManager writes to configured location (consistent behavior)

### 3. Configuration Hierarchy

1. **Settings** (`settings.toml`) - Persistent defaults
2. **GeneratorConfig** - Runtime overrides
3. Merge at runtime

### 4. Type Safety

- Pydantic models for all configuration
- Type hints throughout
- Validation at boundaries

---

## Comparison to Container Manager

This module follows the same pattern as the dotfiles installer's `container_manager`:

| Container Manager | ColorScheme Generator |
|-------------------|----------------------|
| `ContainerEngine` (ABC) | `ColorSchemeGenerator` (ABC) |
| `DockerEngine` | `PywalGenerator` |
| `ImageManager` | `OutputManager` |
| Factory pattern | Factory pattern |
| Dynaconf + Pydantic | Dynaconf + Pydantic |

---

## Status

🚧 **In Development** - Core architecture complete, backend implementations in progress.

**Completed:**
- ✅ Configuration system (dynaconf + Pydantic)
- ✅ Core types and abstractions
- ✅ OutputManager implementation
- ✅ Exception hierarchy
- ✅ Factory pattern
- ✅ All three backends (pywal, wallust, custom)
- ✅ Jinja2 templates
- ✅ CLI interface
- ✅ Documentation

**In Progress:**
- 🚧 Comprehensive testing
- 🚧 Additional output formats (TOML)
- 🚧 Advanced features (color adjustment, palette generation)

---

## Related Projects

- [pywal](https://github.com/dylanaraps/pywal) - Generate and change color-schemes
- [wallust](https://codeberg.org/explosion-mental/wallust) - Rust-based color scheme generator
- [matugen](https://github.com/InioX/matugen) - Material You color generation

---

## License

MIT

---

## Contributing

This is part of a larger dotfiles system. See the main repository for contribution guidelines.

---

**Navigation:**
- [Diagrams](diagrams/) - 📊 50+ Mermaid diagrams
- [Architecture](architecture/) - Design and structure
- [API Reference](api/) - Detailed API documentation
- [Guides](guides/) - Practical usage guides
- [Reference](reference/) - Additional reference material


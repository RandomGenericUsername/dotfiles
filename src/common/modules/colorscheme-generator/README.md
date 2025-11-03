# Colorscheme Generator

Generate color schemes from images using multiple backends (pywal, wallust, custom).

## Features

- 🎨 **Multiple Backends** - Pywal, Wallust, or custom Python implementation
- 📁 **Multiple Formats** - JSON, Shell, CSS, YAML, TOML
- ⚙️ **Flexible Configuration** - Settings file + runtime overrides
- 🔧 **Clean Architecture** - Separation between color extraction and file generation
- 🚀 **Type Safe** - Full Pydantic validation
- 📦 **Isolated Project** - Independent UV project with own dependencies

## Architecture

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

## Installation

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

## Quick Start

```python
from pathlib import Path
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.types import GeneratorConfig
from colorscheme_generator.config.enums import Backend, ColorFormat

# Load settings
settings = Settings.get()

# Create config
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.PYWAL,
    output_dir=Path("~/.cache/colorscheme"),
    formats=[ColorFormat.JSON, ColorFormat.CSS]
)

# Extract colors (once backends are implemented)
# from colorscheme_generator import ColorSchemeGeneratorFactory
# generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
# scheme = generator.generate(Path("~/wallpapers/mountain.png"), config)

# Write files
# from colorscheme_generator.core.managers import OutputManager
# output_manager = OutputManager(settings)
# output_files = output_manager.write_outputs(scheme, config.output_dir, config.formats)

# print(f"Generated: {output_files}")
```

## Configuration

### Settings File (`config/settings.toml`)

```toml
# Output configuration
[output]
directory = "$HOME/.cache/colorscheme"
formats = ["json", "sh", "css", "yaml"]

# Generation defaults
[generation]
default_backend = "pywal"
default_color_count = 16
saturation_adjustment = 1.0

# Backend-specific settings
[backends.pywal]
cache_dir = "$HOME/.cache/wal"
use_library = true

[backends.wallust]
output_format = "json"
backend_type = "resized"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16

# Template configuration
[templates]
directory = "templates"
strict_mode = true
```

### Runtime Overrides

```python
# Override settings at runtime
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.WALLUST,
    output_dir=Path("/tmp/colors"),
    color_count=32
)
```

## Backends

### Pywal

- **Language**: Python
- **Speed**: Medium
- **Quality**: Excellent
- **Installation**: `pip install pywal`

### Wallust

- **Language**: Rust
- **Speed**: Fast
- **Quality**: Excellent
- **Installation**: `cargo install wallust`

### Custom

- **Language**: Python (PIL)
- **Speed**: Slow
- **Quality**: Good
- **Installation**: Built-in (no external deps)

See [docs/backends.md](docs/backends.md) for detailed comparison.

## Output Formats

### JSON
```json
{
  "background": "#1a1a1a",
  "foreground": "#ffffff",
  "colors": ["#000000", "#ff0000", ...]
}
```

### Shell
```bash
background="#1a1a1a"
foreground="#ffffff"
color0="#000000"
```

### CSS
```css
:root {
  --background: #1a1a1a;
  --foreground: #ffffff;
  --color0: #000000;
}
```

## Documentation

- [Architecture](docs/architecture.md) - Design and component overview
- [Configuration](docs/configuration.md) - Settings and configuration guide
- [Usage](docs/usage.md) - Usage examples and API reference
- [Backends](docs/backends.md) - Backend comparison and selection guide

## Development

### Setup

```bash
# Install development dependencies
make install

# Run tests
make test

# Format code
make format

# Type check
make type-check

# Lint
make lint
```

### Project Structure

```
src/dotfiles/modules/colorscheme_generator/
├── config/
│   └── settings.toml              # Configuration file
├── src/colorscheme_generator/
│   ├── config/                    # Configuration module
│   │   ├── enums.py
│   │   ├── defaults.py
│   │   ├── config.py              # Pydantic models
│   │   └── settings.py            # Dynaconf loader
│   ├── core/                      # Core abstractions
│   │   ├── base.py                # Abstract base class
│   │   ├── types.py               # ColorScheme, Color, etc.
│   │   ├── exceptions.py
│   │   └── managers/
│   │       └── output_manager.py  # File writing
│   ├── backends/                  # Backend implementations
│   │   ├── pywal.py
│   │   ├── wallust.py
│   │   └── custom.py
│   ├── factory.py                 # Factory pattern
│   └── utils/                     # Utilities
├── templates/                     # Jinja2 templates
│   ├── colors.json.j2
│   ├── colors.sh.j2
│   └── colors.css.j2
├── docs/                          # Documentation
├── tests/                         # Tests
└── examples/                      # Usage examples
```

## Design Principles

### Separation of Concerns

- **Backends** extract colors → return `ColorScheme` object
- **OutputManager** writes `ColorScheme` → files
- Clean separation, no coupling

### Backend Independence

- Pywal writes to `~/.cache/wal/` (we just read from there)
- Wallust outputs JSON to stdout (we parse it)
- Custom uses PIL (full control)
- OutputManager writes to configured location (consistent behavior)

### Configuration Hierarchy

1. **Settings** (`settings.toml`) - Persistent defaults
2. **GeneratorConfig** - Runtime overrides
3. Merge at runtime

### Type Safety

- Pydantic models for all configuration
- Type hints throughout
- Validation at boundaries

## Comparison to Installer Pattern

This module follows the same pattern as the dotfiles installer's `container_manager`:

| Container Manager | ColorScheme Generator |
|-------------------|----------------------|
| `ContainerEngine` (ABC) | `ColorSchemeGenerator` (ABC) |
| `DockerEngine` | `PywalGenerator` |
| `ImageManager` | `OutputManager` |
| Factory pattern | Factory pattern |
| Dynaconf + Pydantic | Dynaconf + Pydantic |

## License

MIT

## Contributing

This is part of a larger dotfiles system. See the main repository for contribution guidelines.

## Status

🚧 **In Development** - Core architecture complete, backend implementations in progress.

**Completed:**
- ✅ Configuration system (dynaconf + Pydantic)
- ✅ Core types and abstractions
- ✅ OutputManager implementation
- ✅ Exception hierarchy
- ✅ Documentation

**In Progress:**
- 🚧 Backend implementations (pywal, wallust, custom)
- 🚧 Factory pattern
- 🚧 Jinja2 templates
- 🚧 Tests
- 🚧 CLI interface

## Related Projects

- [pywal](https://github.com/dylanaraps/pywal) - Generate and change color-schemes
- [wallust](https://codeberg.org/explosion-mental/wallust) - Rust-based color scheme generator
- [matugen](https://github.com/InioX/matugen) - Material You color generation

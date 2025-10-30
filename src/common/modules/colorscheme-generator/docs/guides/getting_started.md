# Getting Started

**Module:** `colorscheme_generator`  
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Basic Concepts](#basic-concepts)
4. [First Steps](#first-steps)
5. [Common Workflows](#common-workflows)

---

## Installation

### Prerequisites

- Python 3.10+
- UV package manager (recommended) or pip

### Install Module

```bash
cd src/dotfiles/modules/colorscheme_generator

# Create virtual environment
uv venv

# Install module
uv sync
uv pip install -e .
```

### Optional Dependencies

#### Pywal Backend

```bash
# Install pywal library
uv pip install -e ".[pywal]"

# Or install pywal CLI
pip install pywal
```

#### Wallust Backend

```bash
# Install wallust (Rust binary)
cargo install wallust
```

#### Development Tools

```bash
# Install development dependencies
uv pip install -e ".[dev]"
```

### Verify Installation

```python
from colorscheme_generator import ColorSchemeGeneratorFactory
from colorscheme_generator.config.settings import Settings

# List available backends
settings = Settings.get()
available = ColorSchemeGeneratorFactory.list_available(settings)
print(f"Available backends: {', '.join(available)}")
# Output: Available backends: custom
# (or: wallust, pywal, custom if installed)
```

---

## Quick Start

### 5-Minute Tutorial

```python
from pathlib import Path
from colorscheme_generator import (
    ColorSchemeGeneratorFactory,
    OutputManager,
    Settings,
    GeneratorConfig,
    ColorFormat,
)

# 1. Load settings
settings = Settings.get()

# 2. Create generator (auto-detect best backend)
generator = ColorSchemeGeneratorFactory.create_auto(settings)
print(f"Using backend: {generator.backend_name}")

# 3. Create configuration
config = GeneratorConfig.from_settings(
    settings,
    output_dir=Path("~/.cache/colorscheme").expanduser(),
    formats=[ColorFormat.JSON, ColorFormat.CSS]
)

# 4. Generate colors from image
image_path = Path("~/wallpapers/mountain.png").expanduser()
scheme = generator.generate(image_path, config)

# 5. Write to files
manager = OutputManager(settings)
output_files = manager.write_outputs(
    scheme,
    config.output_dir,
    config.formats
)

# 6. View results
print(f"Background: {scheme.background.hex}")
print(f"Foreground: {scheme.foreground.hex}")
print(f"Generated files: {list(output_files.values())}")
```

### CLI Quick Start

```bash
# Generate with auto-detected backend
colorscheme-gen ~/wallpapers/mountain.png

# Use specific backend
colorscheme-gen ~/wallpapers/mountain.png --backend pywal

# Custom output directory and formats
colorscheme-gen ~/wallpapers/mountain.png \
    --output-dir ~/.config/colors \
    --formats json css sh

# List available backends
colorscheme-gen --list-backends
```

---

## Basic Concepts

### Two-Layer Architecture

The module separates color extraction from file generation:

```
Layer 1: Backends → Extract colors → ColorScheme object
Layer 2: OutputManager → Write ColorScheme → Files
```

**Why?**
- Backends focus on color extraction
- OutputManager focuses on file writing
- No coupling between layers

### Key Components

#### 1. Backends (Layer 1)

Extract colors from images:

- **PywalGenerator** - Uses pywal (Python/CLI)
- **WallustGenerator** - Uses wallust (Rust binary)
- **CustomGenerator** - Uses PIL + scikit-learn (always available)

#### 2. OutputManager (Layer 2)

Writes ColorScheme to files:

- Uses Jinja2 templates
- Supports multiple formats (JSON, CSS, Shell, YAML)
- Independent of backends

#### 3. Configuration

Two levels:

- **Settings** (`settings.toml`) - Persistent defaults
- **GeneratorConfig** - Runtime overrides

#### 4. Factory

Creates backend instances:

- `create(backend, settings)` - Create specific backend
- `create_auto(settings)` - Auto-detect best backend

---

## First Steps

### Step 1: Understand Settings

**Location:** `cli/config/settings.toml` (or module-specific)

```toml
[output]
directory = "$HOME/.cache/colorscheme"
formats = ["json", "css", "sh"]

[generation]
default_backend = "pywal"
color_count = 16

[backends.pywal]
use_library = true
cache_dir = "$HOME/.cache/wal"
```

**Load settings:**
```python
from colorscheme_generator.config.settings import Settings

settings = Settings.get()
print(settings.output.directory)  # PosixPath('/home/user/.cache/colorscheme')
```

### Step 2: Choose a Backend

**Check availability:**
```python
from colorscheme_generator.factory import ColorSchemeGeneratorFactory
from colorscheme_generator.config.enums import Backend

settings = Settings.get()

# Check specific backend
pywal_gen = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
if pywal_gen.is_available():
    print("Pywal is available")

# Or auto-detect
generator = ColorSchemeGeneratorFactory.create_auto(settings)
print(f"Using: {generator.backend_name}")
```

### Step 3: Generate Colors

```python
from pathlib import Path
from colorscheme_generator.core.types import GeneratorConfig

# Create config
config = GeneratorConfig.from_settings(settings)

# Generate colors
image_path = Path("~/wallpapers/sunset.png").expanduser()
scheme = generator.generate(image_path, config)

# Inspect colors
print(f"Background: {scheme.background.hex}")
print(f"Foreground: {scheme.foreground.hex}")
print(f"Color 0 (black): {scheme.colors[0].hex}")
print(f"Color 1 (red): {scheme.colors[1].hex}")
```

### Step 4: Write Output Files

```python
from colorscheme_generator.core.managers.output_manager import OutputManager
from colorscheme_generator.config.enums import ColorFormat

# Create output manager
manager = OutputManager(settings)

# Write files
output_files = manager.write_outputs(
    scheme,
    Path("~/.config/colors").expanduser(),
    [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.SHELL]
)

# Check results
for fmt, path in output_files.items():
    print(f"{fmt}: {path}")
```

---

## Common Workflows

### Workflow 1: Simple Generation

**Use case:** Generate colors with defaults

```python
from pathlib import Path
from colorscheme_generator import (
    ColorSchemeGeneratorFactory,
    OutputManager,
    Settings,
    GeneratorConfig,
)

settings = Settings.get()
generator = ColorSchemeGeneratorFactory.create_auto(settings)
config = GeneratorConfig.from_settings(settings)

scheme = generator.generate(Path("~/wallpapers/image.png").expanduser(), config)

manager = OutputManager(settings)
output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
```

### Workflow 2: Custom Configuration

**Use case:** Override settings at runtime

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

settings = Settings.get()

# Override settings
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.CUSTOM,
    output_dir=Path("/tmp/colors"),
    formats=[ColorFormat.JSON, ColorFormat.YAML],
    color_count=24,
    backend_options={"algorithm": "median_cut"}
)

generator = ColorSchemeGeneratorFactory.create(config.backend, settings)
scheme = generator.generate(Path("~/wallpapers/image.png").expanduser(), config)

manager = OutputManager(settings)
output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
```

### Workflow 3: Multiple Images

**Use case:** Process multiple images

```python
from pathlib import Path
from colorscheme_generator import (
    ColorSchemeGeneratorFactory,
    OutputManager,
    Settings,
    GeneratorConfig,
)

settings = Settings.get()
generator = ColorSchemeGeneratorFactory.create_auto(settings)
manager = OutputManager(settings)

images = [
    Path("~/wallpapers/mountain.png"),
    Path("~/wallpapers/ocean.png"),
    Path("~/wallpapers/forest.png"),
]

for image in images:
    image = image.expanduser()
    
    # Create config with image-specific output dir
    config = GeneratorConfig.from_settings(
        settings,
        output_dir=Path(f"~/.cache/colorscheme/{image.stem}").expanduser()
    )
    
    # Generate and write
    scheme = generator.generate(image, config)
    output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
    
    print(f"Processed {image.name}: {len(output_files)} files")
```

### Workflow 4: Error Handling

**Use case:** Robust generation with fallbacks

```python
from pathlib import Path
from colorscheme_generator import (
    ColorSchemeGeneratorFactory,
    OutputManager,
    Settings,
    GeneratorConfig,
    Backend,
)
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
)

settings = Settings.get()

# Try preferred backend with fallback
try:
    generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
    generator.ensure_available()
except BackendNotAvailableError:
    print("Pywal not available, using custom backend")
    generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)

# Generate with error handling
try:
    config = GeneratorConfig.from_settings(settings)
    scheme = generator.generate(Path("~/wallpapers/image.png").expanduser(), config)
    
    manager = OutputManager(settings)
    output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
    
    print(f"Success! Generated {len(output_files)} files")
except InvalidImageError as e:
    print(f"Invalid image: {e.image_path}")
except ColorExtractionError as e:
    print(f"Extraction failed: {e}")
```

---

## Next Steps

### Learn More

- **[Usage Patterns](usage_patterns.md)** - Common patterns and best practices
- **[Integration](integration.md)** - Integrate with other modules
- **[Templates](templates.md)** - Working with Jinja2 templates

### API Reference

- **[Core API](../api/core.md)** - Core abstractions and types
- **[Backends API](../api/backends.md)** - Backend implementations
- **[Configuration API](../api/configuration.md)** - Configuration system

### Examples

- **[Examples](../reference/examples.md)** - Comprehensive code examples
- **[Troubleshooting](../reference/troubleshooting.md)** - Common issues and solutions

---

## Tips

### Tip 1: Use Auto-Detection

Let the factory choose the best backend:

```python
generator = ColorSchemeGeneratorFactory.create_auto(settings)
```

### Tip 2: Override Selectively

Only override what you need:

```python
config = GeneratorConfig.from_settings(
    settings,
    output_dir=Path("/tmp/colors")  # Only override output_dir
)
```

### Tip 3: Check Availability

Always check backend availability before use:

```python
if generator.is_available():
    scheme = generator.generate(image_path, config)
```

### Tip 4: Use Context Managers

For file operations, consider using context managers:

```python
from pathlib import Path

output_dir = Path("/tmp/colors")
output_dir.mkdir(parents=True, exist_ok=True)

# Now safe to write
output_files = manager.write_outputs(scheme, output_dir, formats)
```

### Tip 5: Inspect ColorScheme

Explore the generated ColorScheme:

```python
scheme = generator.generate(image_path, config)

print(f"Backend: {scheme.backend}")
print(f"Source: {scheme.source_image}")
print(f"Generated: {scheme.generated_at}")
print(f"Background: {scheme.background.hex} (RGB: {scheme.background.rgb})")
print(f"16 colors: {[c.hex for c in scheme.colors]}")
```


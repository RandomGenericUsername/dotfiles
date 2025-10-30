# Wallpaper Processing System - Implementation Summary

## Overview

A complete container-based wallpaper processing system consisting of:

1. **wallpaper-processor** - Python module for applying effects to wallpapers
2. **wallpaper-orchestrator** - CLI tool for container-based processing

## Architecture

### wallpaper-processor Module

**Location:** `src/common/modules/wallpaper-processor/`

**Purpose:** Core library for applying image effects (blur, brightness, saturation, vignette, color overlay)

**Key Components:**
- **Effect Backends**: Hybrid implementation (ImageMagick + PIL fallback)
  - `blur.py` - Gaussian blur effect
  - `brightness.py` - Brightness adjustment
  - `saturation.py` - Color saturation adjustment
  - `vignette.py` - Edge darkening effect
  - `color_overlay.py` - Color overlay with opacity

- **Pipeline System**: Chain multiple effects together
  - Memory mode (fast, higher memory usage)
  - File mode (slower, memory efficient)

- **Factory Pattern**: Create effects with backend preference
  - Prefers ImageMagick if available
  - Falls back to PIL (always available)
  - Strict mode option

- **Configuration**: Pydantic models + Dynaconf
  - Module settings in `config/settings.toml`
  - User presets in `~/.config/wallpaper-processor/presets.toml`

- **Presets**: Pre-configured effect combinations
  - `dark_blur` - Blurred and darkened
  - `aesthetic` - Reduced saturation + vignette
  - `lockscreen` - Heavily blurred and darkened
  - `minimal_dark` - Desaturated and darkened

**Dependencies:**
- pydantic (data validation)
- pillow (image processing)
- dynaconf (configuration)
- dotfiles-logging (logging)

**Installation:**
```bash
cd src/common/modules/wallpaper-processor
make install
```

**Usage:**
```python
from wallpaper_processor import EffectFactory, get_default_config

config = get_default_config()
pipeline = EffectFactory.create_from_preset("dark_blur", config)
pipeline.apply(input_path, output_path)
```

### wallpaper-orchestrator Tool

**Location:** `src/common/tools/wallpaper-orchestrator/`

**Purpose:** Container-based CLI tool for processing wallpapers

**Key Components:**
- **Container Registry**: Manages container images
- **Container Builder**: Builds wallpaper-processor container
- **Container Runner**: Executes processing in containers
- **Orchestrator**: Coordinates workflow
- **CLI**: User interface (Typer + Rich)

**Container Architecture:**
- Base image: `python:3.12-slim`
- System dependencies: ImageMagick
- Python modules: wallpaper-processor, dotfiles-logging
- Volume mounts: Input (read-only), Output (read-write)
- Environment variables: Configuration passed to container

**Dependencies:**
- typer (CLI framework)
- rich (terminal output)
- pydantic (data validation)
- dynaconf (configuration)
- dotfiles-container-manager (container abstraction)
- wallpaper-processor (processing module)
- dotfiles-logging (logging)

**Installation:**
```bash
cd src/common/tools/wallpaper-orchestrator
make install
```

**Usage:**
```bash
# Single image
wallpaper-process process -i input.jpg -o output.jpg --preset dark_blur

# Batch processing
wallpaper-process batch \
  --batch-dir ~/wallpapers/ \
  --output-dir ~/processed/ \
  --preset aesthetic \
  --parallel 4

# List options
wallpaper-process list
wallpaper-process presets
```

## Design Decisions

### 1. Effect Application Strategy
- **Configurable**: Both in-memory and file-based modes
- **Default**: Memory mode (faster, better quality)
- **File mode**: For large images or memory-constrained environments

### 2. Backend Organization
- **Hybrid approach**: Each effect file contains both ImageMagick and PIL implementations
- **Preference**: ImageMagick preferred, PIL fallback
- **Availability checking**: Runtime dependency detection

### 3. Container I/O
- **Volume mounts**: Following colorscheme-orchestrator pattern
- **Input**: Mounted read-only to `/input/image`
- **Output**: Mounted read-write to `/output`
- **Configuration**: Passed via environment variables

### 4. Preset System
- **Module defaults**: In `config/settings.toml`
- **User overrides**: In `~/.config/wallpaper-orchestrator/presets.toml`
- **Merge behavior**: User presets override module presets

### 5. Batch Processing
- **Sequential**: Default, processes one at a time
- **Parallel**: Configurable worker count
- **Error handling**: Continue on error (configurable)
- **Skip existing**: Optional

## File Structure

```
src/common/
├── modules/
│   └── wallpaper-processor/
│       ├── config/
│       │   └── settings.toml
│       ├── docs/
│       │   ├── api/
│       │   │   └── effects.md
│       │   └── guides/
│       │       └── getting_started.md
│       ├── src/wallpaper_processor/
│       │   ├── backends/
│       │   │   ├── blur.py
│       │   │   ├── brightness.py
│       │   │   ├── saturation.py
│       │   │   ├── vignette.py
│       │   │   └── color_overlay.py
│       │   ├── config/
│       │   │   ├── config.py
│       │   │   ├── enums.py
│       │   │   ├── defaults.py
│       │   │   └── settings.py
│       │   ├── core/
│       │   │   ├── base.py
│       │   │   ├── types.py
│       │   │   ├── exceptions.py
│       │   │   └── managers/
│       │   │       ├── preset.py
│       │   │       └── output.py
│       │   ├── pipeline.py
│       │   ├── factory.py
│       │   ├── cli.py
│       │   └── __init__.py
│       ├── tests/
│       │   ├── test_effects.py
│       │   ├── test_pipeline.py
│       │   └── test_factory.py
│       ├── pyproject.toml
│       ├── Makefile
│       └── README.md
│
└── tools/
    └── wallpaper-orchestrator/
        ├── config/
        │   └── settings.toml
        ├── container/
        │   ├── Dockerfile
        │   └── entrypoint.py
        ├── docs/
        │   └── usage.md
        ├── src/wallpaper_orchestrator/
        │   ├── containers/
        │   │   ├── registry.py
        │   │   ├── builder.py
        │   │   └── runner.py
        │   ├── config.py
        │   ├── orchestrator.py
        │   ├── cli.py
        │   └── __init__.py
        ├── tests/
        │   ├── test_config.py
        │   └── test_orchestrator.py
        ├── pyproject.toml
        ├── Makefile
        └── README.md
```

## Testing

### wallpaper-processor Tests
```bash
cd src/common/modules/wallpaper-processor
make test
```

Tests cover:
- Effect implementations (PIL and ImageMagick)
- Pipeline (memory and file modes)
- Factory (effect creation, presets)
- Configuration loading

### wallpaper-orchestrator Tests
```bash
cd src/common/tools/wallpaper-orchestrator
make test
```

Tests cover:
- Configuration management
- Orchestrator initialization
- Component integration

## Documentation

### wallpaper-processor
- **README.md**: Overview, installation, quick start
- **docs/api/effects.md**: Effect API reference
- **docs/guides/getting_started.md**: Comprehensive usage guide

### wallpaper-orchestrator
- **README.md**: Overview, installation, features
- **docs/usage.md**: Complete CLI reference and examples

## Next Steps

To use the system:

1. **Install wallpaper-processor module:**
   ```bash
   cd src/common/modules/wallpaper-processor
   make install
   ```

2. **Install wallpaper-orchestrator tool:**
   ```bash
   cd src/common/tools/wallpaper-orchestrator
   make install
   ```

3. **Build container image:**
   ```bash
   wallpaper-process build
   ```

4. **Process wallpapers:**
   ```bash
   wallpaper-process process -i input.jpg -o output.jpg --preset dark_blur
   ```

## Integration with Dotfiles

The wallpaper processing system can be integrated into the dotfiles installer:

1. **Runtime Dependencies**: Install wallpaper-processor in dotfiles runtime venv
2. **Wallpaper Setup**: Use orchestrator to process wallpapers during installation
3. **Dynamic Updates**: Process wallpapers on-the-fly based on colorscheme

Example integration:
```python
# In dotfiles installer
from wallpaper_orchestrator import WallpaperOrchestrator, get_default_config

config = get_default_config()
orchestrator = WallpaperOrchestrator(config)

# Process wallpaper with current colorscheme
orchestrator.process_image(
    input_path=wallpaper_path,
    output_path=processed_path,
    preset="dark_blur"
)
```


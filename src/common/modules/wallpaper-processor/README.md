# Wallpaper Processor

Apply effects to wallpapers using ImageMagick and PIL backends with a clean, extensible architecture.

## Features

- 🎨 **Multiple Effects**: Blur, brightness, saturation, vignette, color overlay, grayscale, negate
- 🔧 **Dual Backends**: ImageMagick (preferred) with PIL fallback
- 📦 **Presets**: Pre-configured effect combinations
- 🔄 **Pipeline**: Chain multiple effects together
- ⚡ **Flexible Processing**: In-memory (fast) or file-based (memory-efficient)
- 🎯 **Type-Safe**: Pydantic models for all parameters
- 📝 **Logging**: Integrated with dotfiles-logging module
- 🎭 **Variant Generation**: Generate all effect variants automatically

## Installation

This module is used as a path dependency within the dotfiles project:

```toml
[project]
dependencies = [
    "wallpaper-processor @ file://../../common/modules/wallpaper-processor",
]
```

Or install directly:

```bash
# From the wallpaper-processor directory
make install
```

## Quick Start

### Programmatic Usage

```python
from wallpaper_processor import EffectFactory, EffectPipeline, ProcessorConfig
from wallpaper_processor.core.types import BlurParams, BrightnessParams
from wallpaper_processor.config import AppConfig
from pathlib import Path

# Load configuration
config = AppConfig()

# Create effects
factory = EffectFactory()
blur = factory.create("blur", config)
brightness = factory.create("brightness", config)

# Create pipeline
pipeline = EffectPipeline(
    effects=[
        (blur, BlurParams(sigma=6)),
        (brightness, BrightnessParams(adjustment=-15)),
    ],
    config=ProcessorConfig(processing_mode="memory")
)

# Apply effects
pipeline.apply(
    input_path=Path("wallpaper.jpg"),
    output_path=Path("processed.jpg")
)
```

### Using Presets

```python
from wallpaper_processor import EffectFactory
from wallpaper_processor.config import AppConfig
from pathlib import Path

config = AppConfig()
pipeline = EffectFactory.create_from_preset("dark_blur", config)

pipeline.apply(
    input_path=Path("wallpaper.jpg"),
    output_path=Path("processed.jpg")
)
```

### CLI Usage

```bash
# Single effect
wallpaper-process process -i input.jpg -o output.jpg -e blur --sigma 8

# Multiple effects
wallpaper-process process -i input.jpg -o output.jpg \
  -e blur --sigma 6 \
  -e brightness --adjustment -15

# Use preset
wallpaper-process process -i input.jpg -o output.jpg --preset dark_blur

# Use preset with overrides
wallpaper-process process -i input.jpg -o output.jpg --preset dark_blur --sigma 10

# Generate all effect variants
wallpaper-process variants -i input.jpg -o /tmp/wallpapers
# Creates: /tmp/wallpapers/input/blur.png, /tmp/wallpapers/input/grayscale.png, etc.
```

## Available Effects

| Effect | Parameters | Description |
|--------|-----------|-------------|
| `blur` | `sigma`, `radius` | Gaussian blur effect |
| `brightness` | `adjustment` | Adjust brightness (-100 to 100) |
| `saturation` | `adjustment` | Adjust saturation (-100 to 100) |
| `vignette` | `strength` | Add vignette effect (0 to 100) |
| `color_overlay` | `color`, `opacity` | Overlay a color with opacity |
| `grayscale` | `method` | Convert to grayscale (average, luminosity, mean) |
| `negate` | - | Invert colors |

## Presets

Presets are defined in `config/settings.toml`:

- **`dark_blur`**: Blurred and darkened for better text readability
- **`aesthetic`**: Aesthetic vaporwave style
- **`lockscreen`**: Heavy blur for lockscreen backgrounds
- **`minimal_dark`**: Subtle darkening with slight blur

You can add custom presets in `~/.config/wallpaper-processor/presets.toml`.

## Configuration

Settings are in `config/settings.toml`:

```toml
[processing]
mode = "memory"  # "memory" or "file"
output_format = "png"
quality = 95

[backend]
prefer_imagemagick = true
strict_mode = false
fallback_enabled = true

[defaults.blur]
radius = 0
sigma = 8

[presets.dark_blur]
description = "Blurred and darkened"
effects = [
    { name = "blur", params = { sigma = 6 } },
    { name = "brightness", params = { adjustment = -15 } },
]
```

## Architecture

```
wallpaper-processor/
├── config/
│   └── settings.toml          # Presets and defaults
├── src/wallpaper_processor/
│   ├── config/                # Configuration system
│   ├── core/                  # Core abstractions
│   │   ├── base.py           # WallpaperEffect ABC
│   │   ├── types.py          # Pydantic models
│   │   └── managers/         # Preset & output managers
│   ├── backends/             # Effect implementations
│   │   ├── blur.py          # ImageMagick + PIL blur
│   │   ├── brightness.py    # ImageMagick + PIL brightness
│   │   └── ...
│   ├── pipeline.py          # EffectPipeline
│   ├── factory.py           # EffectFactory
│   └── cli.py               # CLI interface
└── tests/                   # Comprehensive tests
```

## Adding New Effects

1. Create a new file in `backends/` (e.g., `my_effect.py`)
2. Implement both ImageMagick and PIL versions
3. Add default parameters to `config/settings.toml`
4. Register in `factory.py`

See [docs/guides/creating_effects.md](docs/guides/creating_effects.md) for details.

## Documentation

- [API Reference](docs/api/)
- [User Guides](docs/guides/)
- [Examples](docs/reference/examples.md)

## Development

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Lint
make lint

# Clean
make clean
```

## License

MIT

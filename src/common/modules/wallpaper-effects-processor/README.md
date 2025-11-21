# Wallpaper Effects Processor

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
- 🚀 **Dynamic Registry**: Auto-discovery of effects - add new effects with just a decorator!

## Installation

This module is used as a path dependency within the dotfiles project:

```toml
[project]
dependencies = [
    "wallpaper-effects-processor @ file://../../common/modules/wallpaper-effects-processor",
]
```

Or install directly:

```bash
# From the wallpaper-effects-processor directory
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
wallpaper-effects-process process -i input.jpg -o output.jpg -e blur --sigma 8

# Multiple effects
wallpaper-effects-process process -i input.jpg -o output.jpg \
  -e blur --sigma 6 \
  -e brightness --adjustment -15

# Use preset
wallpaper-effects-process process -i input.jpg -o output.jpg --preset dark_blur

# Use preset with overrides
wallpaper-effects-process process -i input.jpg -o output.jpg --preset dark_blur --sigma 10

# Generate all effect variants
wallpaper-effects-process variants -i input.jpg -o /tmp/wallpapers
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

You can add custom presets in `~/.config/wallpaper-effects-processor/presets.toml`.

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

The module uses a **Registry Pattern with Auto-Discovery** for maximum extensibility:

```
wallpaper-effects-processor/
├── config/
│   └── settings.toml          # Presets and defaults
├── src/wallpaper_processor/
│   ├── config/                # Configuration system
│   ├── core/                  # Core abstractions
│   │   ├── base.py           # WallpaperEffect ABC
│   │   ├── types.py          # Pydantic models
│   │   ├── registry/         # 🆕 Registry system
│   │   │   ├── effect_registry.py  # Central registry
│   │   │   └── decorators.py       # @register_effect()
│   │   └── managers/         # Preset & output managers
│   ├── backends/             # Effect implementations
│   │   ├── __init__.py      # 🆕 Auto-discovery via pkgutil
│   │   ├── blur.py          # ImageMagick + PIL blur
│   │   ├── brightness.py    # ImageMagick + PIL brightness
│   │   └── ...
│   ├── pipeline.py          # EffectPipeline
│   ├── factory.py           # EffectFactory (registry-based)
│   └── cli.py               # CLI interface
└── tests/                   # Comprehensive tests
```

### Key Components

- **EffectRegistry**: Central registry for all effects and parameters
- **@register_effect()**: Decorator for automatic effect registration
- **Auto-Discovery**: Effects are automatically discovered at import time
- **EffectFactory**: Creates effects by querying the registry (no hardcoded lists!)

## Adding New Effects

**The registry-based architecture makes adding new effects incredibly simple!**

### Quick Example

Create a new file `backends/sepia.py`:

```python
from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.types import EffectParams
from wallpaper_processor.core.registry import register_effect
from pydantic import Field

# 1. Define parameters (optional if no parameters needed)
class SepiaParams(EffectParams):
    """Parameters for sepia effect."""
    intensity: int = Field(default=80, ge=0, le=100, description="Sepia intensity")

# 2. Implement ImageMagick version
@register_effect("sepia")  # ← That's it! Auto-registered!
class ImageMagickSepia(WallpaperEffect):
    """Sepia effect using ImageMagick."""

    backend_name = "imagemagick"

    def apply(self, input_path: str, output_path: str, params: SepiaParams) -> None:
        intensity = params.intensity
        self._run_imagemagick(
            input_path,
            output_path,
            ["-sepia-tone", f"{intensity}%"]
        )

# 3. Implement PIL version (fallback)
@register_effect("sepia")  # ← Same decorator, different backend!
class PILSepia(WallpaperEffect):
    """Sepia effect using PIL."""

    backend_name = "pil"

    def apply(self, input_path: str, output_path: str, params: SepiaParams) -> None:
        from PIL import Image, ImageOps

        img = Image.open(input_path)
        # Convert to grayscale first
        gray = ImageOps.grayscale(img)
        # Apply sepia toning
        sepia = ImageOps.colorize(gray, "#704214", "#C0A080")
        sepia.save(output_path)
```

**That's it!** Your new effect is now:
- ✅ Automatically discovered and registered
- ✅ Available via `EffectFactory.create("sepia", config)`
- ✅ Listed in `EffectFactory.get_all_effect_names()`
- ✅ Usable in CLI: `wallpaper-effects-process process -i input.jpg -o output.jpg -e sepia --intensity 90`
- ✅ Included in variant generation

### Step-by-Step Guide

1. **Create effect file**: `src/wallpaper_processor/backends/my_effect.py`
2. **Define parameters** (optional):
   ```python
   from wallpaper_processor.core.types import EffectParams
   from pydantic import Field

   class MyEffectParams(EffectParams):
       my_param: int = Field(default=50, ge=0, le=100)
   ```

3. **Implement ImageMagick version**:
   ```python
   from wallpaper_processor.core.base import WallpaperEffect
   from wallpaper_processor.core.registry import register_effect

   @register_effect("my_effect")
   class ImageMagickMyEffect(WallpaperEffect):
       backend_name = "imagemagick"

       def apply(self, input_path: str, output_path: str, params: MyEffectParams) -> None:
           self._run_imagemagick(input_path, output_path, ["-my-operation", str(params.my_param)])
   ```

4. **Implement PIL version**:
   ```python
   @register_effect("my_effect")
   class PILMyEffect(WallpaperEffect):
       backend_name = "pil"

       def apply(self, input_path: str, output_path: str, params: MyEffectParams) -> None:
           from PIL import Image
           img = Image.open(input_path)
           # ... apply effect ...
           img.save(output_path)
   ```

5. **Register parameters** (in `core/types.py`):
   ```python
   from wallpaper_processor.core.registry import EffectRegistry

   EffectRegistry.register_params("my_effect", MyEffectParams)
   ```

6. **Add defaults** (optional, in `config/settings.toml`):
   ```toml
   [defaults.my_effect]
   my_param = 50
   ```

**No factory modifications needed!** The registry handles everything automatically.

### What Changed?

**Before (Hardcoded):**
- Adding an effect required editing 6+ files
- Manual registration in factory if/elif chains
- Hardcoded effect lists
- Easy to forget steps

**After (Registry-Based):**
- Adding an effect requires **1 file** with a decorator
- Automatic registration at import time
- Dynamic effect discovery
- Impossible to forget - just add `@register_effect()`!

See the existing effects in `src/wallpaper_processor/backends/` for complete examples.

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

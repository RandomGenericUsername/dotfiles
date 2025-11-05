# Getting Started with Wallpaper Effects Processor

## Installation

### As a Module Dependency

Add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "wallpaper-effects-processor @ file://../../common/modules/wallpaper-effects-processor",
]
```

### Standalone Installation

```bash
cd src/common/modules/wallpaper-effects-processor
make install
```

## Quick Start

### 1. Basic Usage

```python
from pathlib import Path
from wallpaper_processor import (
    EffectFactory,
    EffectPipeline,
    BlurParams,
    BrightnessParams,
    get_default_config,
)

# Load configuration
config = get_default_config()

# Create effects
factory = EffectFactory()
blur = factory.create("blur", config)
brightness = factory.create("brightness", config)

# Create pipeline
pipeline = EffectPipeline([
    (blur, BlurParams(sigma=6)),
    (brightness, BrightnessParams(adjustment=-15)),
])

# Apply effects
pipeline.apply(
    input_path=Path("wallpaper.jpg"),
    output_path=Path("processed.jpg")
)
```

### 2. Using Presets

```python
from pathlib import Path
from wallpaper_processor import EffectFactory, get_default_config

config = get_default_config()

# Create pipeline from preset
pipeline = EffectFactory.create_from_preset("dark_blur", config)

# Apply
pipeline.apply(
    input_path=Path("wallpaper.jpg"),
    output_path=Path("processed.jpg")
)
```

### 3. CLI Usage

```bash
# Single effect
wallpaper-process -i input.jpg -o output.jpg -e blur --sigma 8

# Multiple effects
wallpaper-process -i input.jpg -o output.jpg \
  -e blur --sigma 6 \
  -e brightness --adjustment -15

# Use preset
wallpaper-process -i input.jpg -o output.jpg --preset dark_blur

# List available effects
wallpaper-process --list-effects

# List presets
wallpaper-process --list-presets
```

## Configuration

### Default Settings

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

### User Configuration

Create `~/.config/wallpaper-processor/presets.toml` for custom presets:

```toml
[presets.my_custom]
description = "My personal preset"
effects = [
    { name = "blur", params = { sigma = 10 } },
    { name = "saturation", params = { adjustment = -50 } },
]
```

## Processing Modes

### Memory Mode (Default)

Loads image once, applies all effects in memory, saves once.

**Pros:**
- Faster
- Better quality (no intermediate compression)

**Cons:**
- Higher memory usage

```python
from wallpaper_processor import ProcessorConfig

config = ProcessorConfig(processing_mode="memory")
pipeline = EffectPipeline(effects, config)
```

### File Mode

Each effect reads from file, writes to temp file.

**Pros:**
- Lower memory usage
- Better for large images

**Cons:**
- Slower
- Potential quality loss from intermediate saves

```python
from wallpaper_processor import ProcessorConfig

config = ProcessorConfig(processing_mode="file")
pipeline = EffectPipeline(effects, config)
```

## Output Formats

Supported formats:
- PNG (lossless)
- JPEG/JPG (lossy)
- WebP (lossy)
- BMP (lossless)
- TIFF (lossless)

### Quality Settings

For lossy formats (JPEG, WebP):

```python
from wallpaper_processor import ProcessorConfig

config = ProcessorConfig(
    output_format="jpeg",
    quality=90  # 1-100
)
```

## Metadata

Generate metadata about processing:

```python
from wallpaper_processor import ProcessorConfig

config = ProcessorConfig(write_metadata=True)
pipeline = EffectPipeline(effects, config)
pipeline.apply(input_path, output_path)

# Metadata written to: output_metadata.json
```

Metadata includes:
- Input/output paths
- Effects applied (name, backend, parameters)
- Processing mode
- Output format and quality

## Error Handling

```python
from wallpaper_processor import (
    EffectNotAvailableError,
    ProcessingError,
    PresetNotFoundError,
)

try:
    pipeline.apply(input_path, output_path)
except FileNotFoundError as e:
    print(f"Input file not found: {e}")
except EffectNotAvailableError as e:
    print(f"Effect not available: {e.effect_name}")
except ProcessingError as e:
    print(f"Processing failed: {e}")
except PresetNotFoundError as e:
    print(f"Preset not found: {e.preset_name}")
```

## Next Steps

- [Effects API Reference](../api/effects.md)
- [Pipeline API Reference](../api/pipeline.md)
- [Creating Custom Effects](creating_effects.md)
- [Examples](../reference/examples.md)

# Creating New Effects

This guide shows you how to add new effects to the wallpaper-effects-processor module using the registry-based architecture.

## Overview

The module uses a **Registry Pattern with Auto-Discovery** that makes adding new effects incredibly simple:

1. Create a single file in `backends/`
2. Add the `@register_effect()` decorator to your effect classes
3. That's it! The effect is automatically discovered and available

## Quick Start

### Minimal Example (No Parameters)

```python
# src/wallpaper_processor/backends/flip.py
from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.registry import register_effect

@register_effect("flip")
class ImageMagickFlip(WallpaperEffect):
    backend_name = "imagemagick"

    def apply(self, input_path: str, output_path: str, params=None) -> None:
        self._run_imagemagick(input_path, output_path, ["-flip"])

@register_effect("flip")
class PILFlip(WallpaperEffect):
    backend_name = "pil"

    def apply(self, input_path: str, output_path: str, params=None) -> None:
        from PIL import Image
        img = Image.open(input_path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img.save(output_path)
```

**Done!** Your effect is now available everywhere.

### Full Example (With Parameters)

```python
# src/wallpaper_processor/backends/rotate.py
from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.types import EffectParams
from wallpaper_processor.core.registry import register_effect
from pydantic import Field

# 1. Define parameters
class RotateParams(EffectParams):
    """Parameters for rotate effect."""
    degrees: float = Field(
        default=90.0,
        ge=-360.0,
        le=360.0,
        description="Rotation angle in degrees"
    )
    background: str = Field(
        default="transparent",
        description="Background color for empty areas"
    )

# 2. ImageMagick implementation
@register_effect("rotate")
class ImageMagickRotate(WallpaperEffect):
    """Rotate image using ImageMagick."""

    backend_name = "imagemagick"

    def apply(self, input_path: str, output_path: str, params: RotateParams) -> None:
        args = [
            "-background", params.background,
            "-rotate", str(params.degrees)
        ]
        self._run_imagemagick(input_path, output_path, args)

# 3. PIL implementation
@register_effect("rotate")
class PILRotate(WallpaperEffect):
    """Rotate image using PIL."""

    backend_name = "pil"

    def apply(self, input_path: str, output_path: str, params: RotateParams) -> None:
        from PIL import Image

        img = Image.open(input_path)
        # PIL rotates counter-clockwise, so negate
        img = img.rotate(-params.degrees, expand=True)
        img.save(output_path)
```

Then register the parameters in `src/wallpaper_processor/core/types.py`:

```python
from wallpaper_processor.core.registry import EffectRegistry
from .rotate import RotateParams  # Import your params

# Add to the registration section
EffectRegistry.register_params("rotate", RotateParams)
```

## Step-by-Step Guide

### Step 1: Create Effect File

Create a new file in `src/wallpaper_processor/backends/`:

```bash
touch src/wallpaper_processor/backends/my_effect.py
```

### Step 2: Define Parameters (Optional)

If your effect needs parameters, define them using Pydantic:

```python
from wallpaper_processor.core.types import EffectParams
from pydantic import Field

class MyEffectParams(EffectParams):
    """Parameters for my_effect."""

    intensity: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Effect intensity (0-100)"
    )

    mode: str = Field(
        default="normal",
        description="Processing mode"
    )
```

**Pydantic Features:**
- Type validation
- Default values
- Range constraints (`ge`, `le`, `gt`, `lt`)
- Custom validators
- JSON schema generation

### Step 3: Implement ImageMagick Version

```python
from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.registry import register_effect

@register_effect("my_effect")  # ← Register with effect name
class ImageMagickMyEffect(WallpaperEffect):
    """My effect using ImageMagick."""

    backend_name = "imagemagick"  # ← Must be "imagemagick"

    def apply(self, input_path: str, output_path: str, params: MyEffectParams) -> None:
        """Apply the effect.

        Args:
            input_path: Path to input image
            output_path: Path to save output image
            params: Effect parameters
        """
        # Build ImageMagick arguments
        args = [
            "-my-operation", str(params.intensity),
            "-mode", params.mode
        ]

        # Use helper method to run ImageMagick
        self._run_imagemagick(input_path, output_path, args)
```

**Helper Methods Available:**
- `self._run_imagemagick(input, output, args)` - Run ImageMagick command
- `self.logger` - Logger instance
- `self.config` - Configuration object

### Step 4: Implement PIL Version

```python
@register_effect("my_effect")  # ← Same effect name, different backend
class PILMyEffect(WallpaperEffect):
    """My effect using PIL."""

    backend_name = "pil"  # ← Must be "pil"

    def apply(self, input_path: str, output_path: str, params: MyEffectParams) -> None:
        """Apply the effect using PIL.

        Args:
            input_path: Path to input image
            output_path: Path to save output image
            params: Effect parameters
        """
        from PIL import Image, ImageEnhance, ImageFilter

        # Load image
        img = Image.open(input_path)

        # Apply effect
        if params.mode == "normal":
            # Example: adjust brightness based on intensity
            enhancer = ImageEnhance.Brightness(img)
            factor = 1.0 + (params.intensity / 100.0)
            img = enhancer.enhance(factor)

        # Save result
        img.save(output_path)
```

**PIL Common Operations:**
- `Image.open(path)` - Load image
- `img.save(path)` - Save image
- `ImageEnhance.Brightness(img)` - Brightness adjustment
- `ImageEnhance.Contrast(img)` - Contrast adjustment
- `ImageEnhance.Color(img)` - Saturation adjustment
- `ImageFilter.GaussianBlur(radius)` - Blur filter
- `ImageOps.grayscale(img)` - Convert to grayscale

### Step 5: Register Parameters

Edit `src/wallpaper_processor/core/types.py` and add your parameter registration:

```python
# At the top, import your params
from wallpaper_processor.backends.my_effect import MyEffectParams

# In the registration section (around line 100+)
EffectRegistry.register_params("my_effect", MyEffectParams)
```

### Step 6: Add Default Configuration (Optional)

Edit `config/settings.toml` to add default values:

```toml
[defaults.my_effect]
intensity = 50
mode = "normal"
```

### Step 7: Test Your Effect

```python
from wallpaper_processor import EffectFactory
from wallpaper_processor.config import AppConfig
from wallpaper_processor.backends.my_effect import MyEffectParams
from pathlib import Path

config = AppConfig()
factory = EffectFactory()

# Create effect
effect = factory.create("my_effect", config)

# Create parameters
params = factory.create_params("my_effect", intensity=75, mode="advanced")

# Apply effect
effect.apply(
    input_path="input.jpg",
    output_path="output.jpg",
    params=params
)
```

## Complete Real-World Example: Sharpen Effect

Here's a complete example implementing a sharpen effect:

```python
# src/wallpaper_processor/backends/sharpen.py
"""Sharpen effect implementation."""

from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.types import EffectParams
from wallpaper_processor.core.registry import register_effect
from pydantic import Field


class SharpenParams(EffectParams):
    """Parameters for sharpen effect."""

    radius: float = Field(
        default=0.0,
        ge=0.0,
        description="Radius of the sharpening operation"
    )
    sigma: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Standard deviation for sharpening"
    )
    amount: float = Field(
        default=1.0,
        ge=0.0,
        le=5.0,
        description="Amount of sharpening to apply"
    )


@register_effect("sharpen")
class ImageMagickSharpen(WallpaperEffect):
    """Sharpen effect using ImageMagick."""

    backend_name = "imagemagick"

    def apply(self, input_path: str, output_path: str, params: SharpenParams) -> None:
        """Apply sharpening using ImageMagick's -sharpen operator.

        Args:
            input_path: Path to input image
            output_path: Path to save sharpened image
            params: Sharpen parameters
        """
        self.logger.debug(
            f"Applying sharpen: radius={params.radius}, "
            f"sigma={params.sigma}, amount={params.amount}"
        )

        # ImageMagick sharpen format: -sharpen radiusxsigma+amount
        sharpen_value = f"{params.radius}x{params.sigma}+{params.amount}"

        self._run_imagemagick(
            input_path,
            output_path,
            ["-sharpen", sharpen_value]
        )


@register_effect("sharpen")
class PILSharpen(WallpaperEffect):
    """Sharpen effect using PIL."""

    backend_name = "pil"

    def apply(self, input_path: str, output_path: str, params: SharpenParams) -> None:
        """Apply sharpening using PIL's UnsharpMask filter.

        Args:
            input_path: Path to input image
            output_path: Path to save sharpened image
            params: Sharpen parameters
        """
        from PIL import Image, ImageFilter

        self.logger.debug(
            f"Applying sharpen (PIL): radius={params.radius}, "
            f"sigma={params.sigma}, amount={params.amount}"
        )

        img = Image.open(input_path)

        # PIL's UnsharpMask: radius, percent, threshold
        # Map our params to PIL's expected values
        percent = int(params.amount * 100)
        threshold = 3

        img = img.filter(
            ImageFilter.UnsharpMask(
                radius=params.sigma,
                percent=percent,
                threshold=threshold
            )
        )

        img.save(output_path)
```

Then register in `core/types.py`:

```python
from wallpaper_processor.backends.sharpen import SharpenParams
EffectRegistry.register_params("sharpen", SharpenParams)
```

And add defaults in `config/settings.toml`:

```toml
[defaults.sharpen]
radius = 0.0
sigma = 1.0
amount = 1.0
```

## Testing Your Effect

Create a test file `tests/test_my_effect.py`:

```python
import pytest
from pathlib import Path
from wallpaper_processor import EffectFactory
from wallpaper_processor.config import AppConfig
from wallpaper_processor.backends.my_effect import MyEffectParams


@pytest.fixture
def factory():
    config = AppConfig()
    return EffectFactory()


def test_my_effect_in_registry(factory):
    """Test that my_effect is registered."""
    effects = factory.get_all_effect_names()
    assert "my_effect" in effects


def test_create_my_effect(factory):
    """Test creating my_effect."""
    config = AppConfig()
    effect = factory.create("my_effect", config)
    assert effect is not None
    assert effect.backend_name in ["imagemagick", "pil"]


def test_my_effect_params(factory):
    """Test creating parameters."""
    params = factory.create_params("my_effect", intensity=75)
    assert isinstance(params, MyEffectParams)
    assert params.intensity == 75


def test_my_effect_apply(factory, tmp_path, sample_image):
    """Test applying the effect."""
    config = AppConfig()
    effect = factory.create("my_effect", config)
    params = factory.create_params("my_effect")

    output_path = tmp_path / "output.png"

    effect.apply(
        input_path=str(sample_image),
        output_path=str(output_path),
        params=params
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
```

Run tests:

```bash
cd src/common/modules/wallpaper-effects-processor
make test
```

## Best Practices

### 1. Always Implement Both Backends

```python
@register_effect("my_effect")
class ImageMagickMyEffect(WallpaperEffect):
    backend_name = "imagemagick"
    # ...

@register_effect("my_effect")
class PILMyEffect(WallpaperEffect):
    backend_name = "pil"
    # ...
```

### 2. Use Descriptive Parameter Names

```python
class MyEffectParams(EffectParams):
    intensity: int = Field(description="Effect intensity (0-100)")  # ✅ Good
    val: int = Field()  # ❌ Bad - unclear
```

### 3. Add Validation

```python
class MyEffectParams(EffectParams):
    intensity: int = Field(default=50, ge=0, le=100)  # ✅ Range validation
    color: str = Field(default="#000000", regex=r"^#[0-9A-Fa-f]{6}$")  # ✅ Format validation
```

### 4. Log Important Operations

```python
def apply(self, input_path: str, output_path: str, params: MyEffectParams) -> None:
    self.logger.debug(f"Applying my_effect with intensity={params.intensity}")
    # ... apply effect ...
    self.logger.debug("Effect applied successfully")
```

### 5. Handle Errors Gracefully

```python
def apply(self, input_path: str, output_path: str, params: MyEffectParams) -> None:
    try:
        # ... apply effect ...
    except Exception as e:
        self.logger.error(f"Failed to apply my_effect: {e}")
        raise
```

## Registry Architecture Benefits

### Before (Hardcoded)
- ❌ Edit 6+ files to add an effect
- ❌ Manual registration in factory
- ❌ Easy to forget steps
- ❌ Hardcoded effect lists

### After (Registry-Based)
- ✅ Edit 1 file with decorator
- ✅ Automatic registration
- ✅ Impossible to forget
- ✅ Dynamic discovery

## Troubleshooting

### Effect Not Showing Up

1. **Check decorator**: Make sure you added `@register_effect("effect_name")`
2. **Check backend_name**: Must be exactly `"imagemagick"` or `"pil"`
3. **Check imports**: Module must be imported (auto-discovery handles this)
4. **Verify registration**:
   ```python
   from wallpaper_processor import EffectFactory
   factory = EffectFactory()
   print(factory.get_all_effect_names())  # Should include your effect
   ```

### Parameters Not Working

1. **Check registration**: Did you add `EffectRegistry.register_params()` in `core/types.py`?
2. **Check inheritance**: Does your params class inherit from `EffectParams`?
3. **Check Pydantic syntax**: Are Field definitions correct?

### Effect Fails at Runtime

1. **Check ImageMagick syntax**: Test command manually: `convert input.jpg -my-operation output.jpg`
2. **Check PIL imports**: Make sure PIL modules are imported inside the method
3. **Check logs**: Use `--log-level debug` to see detailed error messages

## Examples from Existing Effects

See these files for complete examples:
- `backends/blur.py` - Simple effect with radius/sigma params
- `backends/brightness.py` - Adjustment-based effect
- `backends/color_overlay.py` - Effect with color and opacity
- `backends/vignette.py` - Complex multi-step effect
- `backends/grayscale.py` - Effect with mode selection

## Summary

Adding a new effect is now a **3-step process**:

1. **Create file** in `backends/` with `@register_effect()` decorator
2. **Register params** in `core/types.py` (if needed)
3. **Add defaults** in `config/settings.toml` (optional)

The registry handles everything else automatically! 🚀

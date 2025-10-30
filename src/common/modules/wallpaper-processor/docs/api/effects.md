# Effects API Reference

## Available Effects

### Blur

Apply Gaussian blur to wallpapers.

**Parameters:**
- `sigma` (float, 0-100): Blur strength (default: 8)
- `radius` (float, 0-50): Blur radius (default: 0)

**Backends:**
- ImageMagick: Uses `convert -blur radiusxsigma`
- PIL: Uses `ImageFilter.GaussianBlur`

**Example:**
```python
from wallpaper_processor import EffectFactory, BlurParams

config = get_default_config()
blur = EffectFactory.create("blur", config)
params = BlurParams(sigma=10, radius=0)
result = blur.apply(image, params)
```

### Brightness

Adjust image brightness.

**Parameters:**
- `adjustment` (int, -100 to 100): Brightness adjustment percentage (default: -20)
  - Negative values darken
  - Positive values brighten
  - 0 = no change

**Backends:**
- ImageMagick: Uses `convert -brightness-contrast`
- PIL: Uses `ImageEnhance.Brightness`

**Example:**
```python
from wallpaper_processor import EffectFactory, BrightnessParams

config = get_default_config()
brightness = EffectFactory.create("brightness", config)
params = BrightnessParams(adjustment=-30)
result = brightness.apply(image, params)
```

### Saturation

Adjust color saturation.

**Parameters:**
- `adjustment` (int, -100 to 100): Saturation adjustment percentage (default: 0)
  - -100 = grayscale
  - 0 = original
  - 100 = double saturation

**Backends:**
- ImageMagick: Uses `convert -modulate`
- PIL: Uses `ImageEnhance.Color`

**Example:**
```python
from wallpaper_processor import EffectFactory, SaturationParams

config = get_default_config()
saturation = EffectFactory.create("saturation", config)
params = SaturationParams(adjustment=-50)
result = saturation.apply(image, params)
```

### Vignette

Add vignette effect (darkened edges).

**Parameters:**
- `strength` (int, 0-100): Vignette strength (default: 20)

**Backends:**
- ImageMagick: Uses `convert -vignette`
- PIL: Custom radial gradient implementation

**Example:**
```python
from wallpaper_processor import EffectFactory, VignetteParams

config = get_default_config()
vignette = EffectFactory.create("vignette", config)
params = VignetteParams(strength=30)
result = vignette.apply(image, params)
```

### Color Overlay

Overlay a solid color with opacity.

**Parameters:**
- `color` (str): Hex color code (default: "#000000")
- `opacity` (float, 0.0-1.0): Overlay opacity (default: 0.3)

**Backends:**
- ImageMagick: Uses `convert -colorize` with blend
- PIL: Uses `Image.blend`

**Example:**
```python
from wallpaper_processor import EffectFactory, ColorOverlayParams

config = get_default_config()
overlay = EffectFactory.create("color_overlay", config)
params = ColorOverlayParams(color="#ff00ff", opacity=0.2)
result = overlay.apply(image, params)
```

## WallpaperEffect Base Class

All effects inherit from `WallpaperEffect` abstract base class.

### Methods

#### `apply(image: Image.Image, params: EffectParams) -> Image.Image`

Apply effect to PIL Image object.

**Args:**
- `image`: PIL Image object to process
- `params`: Effect parameters (Pydantic model)

**Returns:**
- Modified PIL Image object

**Raises:**
- `ProcessingError`: If effect application fails

#### `apply_to_file(input_path: Path, output_path: Path, params: EffectParams) -> Path`

Apply effect to image file.

**Args:**
- `input_path`: Path to input image file
- `output_path`: Path to output image file
- `params`: Effect parameters

**Returns:**
- Path to output file

**Raises:**
- `FileNotFoundError`: If input file doesn't exist
- `ProcessingError`: If effect application fails

#### `is_available() -> bool`

Check if effect dependencies are available.

**Returns:**
- `True` if effect can be used, `False` otherwise

#### `ensure_available() -> None`

Ensure effect is available, raise if not.

**Raises:**
- `EffectNotAvailableError`: If effect dependencies are not available

### Properties

#### `effect_name -> str`

Get effect identifier (e.g., "blur", "brightness").

#### `backend_name -> str`

Get backend identifier (e.g., "imagemagick", "pil").

#### `get_default_params() -> EffectParams`

Get default parameters for this effect.

## Creating Custom Effects

To create a custom effect:

1. Create a new file in `backends/` (e.g., `my_effect.py`)
2. Implement both ImageMagick and PIL versions
3. Inherit from `WallpaperEffect`
4. Implement all abstract methods
5. Add default parameters to `config/settings.toml`
6. Register in `factory.py`

See [Creating Effects Guide](../guides/creating_effects.md) for details.


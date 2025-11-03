# Core API Reference

**Module:** `colorscheme_generator.core`
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [ColorSchemeGenerator (ABC)](#colorscheme generator-abc)
2. [Color](#color)
3. [ColorScheme](#colorscheme)
4. [GeneratorConfig](#generatorconfig)

---

## ColorSchemeGenerator (ABC)

**Location:** `colorscheme_generator.core.base`

Abstract base class for all color scheme generator backends.

### Class Definition

```python
class ColorSchemeGenerator(ABC):
    """Abstract base class for color scheme generators."""
```

### Abstract Methods

#### generate()

```python
@abstractmethod
def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
    """Generate color scheme from image.

    Args:
        image_path: Path to the source image
        config: Runtime configuration for generation

    Returns:
        ColorScheme object with extracted colors

    Raises:
        InvalidImageError: If image cannot be read or is invalid
        ColorExtractionError: If color extraction fails
        BackendNotAvailableError: If backend is not available
    """
```

**Purpose:** Extract colors from an image and return a ColorScheme object.

**Responsibility:**
- Validate image file
- Extract colors using backend-specific algorithm
- Return standardized ColorScheme object
- Does NOT write output files

**Example:**
```python
generator = PywalGenerator(settings)
scheme = generator.generate(
    Path("~/wallpapers/mountain.png"),
    GeneratorConfig()
)
print(scheme.background.hex)  # '#1a1a1a'
```

#### is_available()

```python
@abstractmethod
def is_available(self) -> bool:
    """Check if backend is available on the system.

    Returns:
        True if backend is available, False otherwise
    """
```

**Purpose:** Check if backend dependencies are installed and accessible.

**Implementation varies by backend:**
- **PywalGenerator:** Checks if `pywal` library or `wal` command exists
- **WallustGenerator:** Checks if `wallust` binary is in PATH
- **CustomGenerator:** Always returns True (PIL is required dependency)

**Example:**
```python
generator = PywalGenerator(settings)
if generator.is_available():
    scheme = generator.generate(image_path, config)
else:
    print("Pywal is not installed")
```

#### backend_name

```python
@property
@abstractmethod
def backend_name(self) -> str:
    """Get the backend name.

    Returns:
        Backend name (e.g., "pywal", "wallust", "custom")
    """
```

**Purpose:** Get string identifier for the backend.

**Used by:** Factory, logging, ColorScheme metadata

**Example:**
```python
generator = PywalGenerator(settings)
print(generator.backend_name)  # 'pywal'
```

### Concrete Methods

#### ensure_available()

```python
def ensure_available(self) -> None:
    """Ensure backend is available, raise error if not.

    Raises:
        BackendNotAvailableError: If backend is not available
    """
```

**Purpose:** Convenience method that calls `is_available()` and raises exception if False.

**Example:**
```python
generator = PywalGenerator(settings)
generator.ensure_available()  # Raises if pywal not installed
```

---

## Color

**Location:** `colorscheme_generator.core.types`

Represents a single color in multiple formats.

### Class Definition

```python
class Color(BaseModel):
    """Single color in multiple formats.

    Attributes:
        hex: Hex color code (e.g., "#FF5733")
        rgb: RGB tuple (0-255 for each channel)
        hsl: Optional HSL tuple (hue: 0-360, saturation: 0-1, lightness: 0-1)
    """
    hex: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    rgb: tuple[int, int, int]
    hsl: tuple[float, float, float] | None = None
```

### Attributes

#### hex
- **Type:** `str`
- **Pattern:** `^#[0-9a-fA-F]{6}$`
- **Description:** Hex color code with # prefix
- **Example:** `"#FF5733"`

#### rgb
- **Type:** `tuple[int, int, int]`
- **Range:** Each value 0-255
- **Description:** RGB color values
- **Example:** `(255, 87, 51)`

#### hsl
- **Type:** `tuple[float, float, float] | None`
- **Range:** Hue 0-360, Saturation 0-1, Lightness 0-1
- **Description:** Optional HSL color values
- **Example:** `(12.0, 1.0, 0.6)`

### Usage Examples

```python
# Create a color
color = Color(hex="#FF5733", rgb=(255, 87, 51))

# Access properties
print(color.hex)  # '#FF5733'
print(color.rgb)  # (255, 87, 51)

# With HSL
color = Color(
    hex="#FF5733",
    rgb=(255, 87, 51),
    hsl=(12.0, 1.0, 0.6)
)
```

### Validation

Pydantic automatically validates:
- Hex pattern matches `#RRGGBB`
- RGB values are integers
- HSL values are floats (if provided)

```python
# Invalid hex - raises ValidationError
color = Color(hex="FF5733", rgb=(255, 87, 51))  # Missing #

# Invalid RGB - raises ValidationError
color = Color(hex="#FF5733", rgb=(255, 87))  # Only 2 values
```

---

## ColorScheme

**Location:** `colorscheme_generator.core.types`

Complete color scheme from an image.

### Class Definition

```python
class ColorScheme(BaseModel):
    """Complete color scheme from image.

    Attributes:
        background: Background color
        foreground: Foreground/text color
        cursor: Cursor color
        colors: List of 16 terminal colors (ANSI colors 0-15)
        source_image: Path to source image
        backend: Backend used for generation
        generated_at: Timestamp of generation
        output_files: Dict of format -> path (populated by OutputManager)
    """
    background: Color
    foreground: Color
    cursor: Color
    colors: list[Color] = Field(..., min_length=16, max_length=16)

    # Metadata
    source_image: Path
    backend: str
    generated_at: datetime = Field(default_factory=datetime.now)

    # Output files (populated by OutputManager)
    output_files: dict[str, Path] = Field(default_factory=dict)
```

### Attributes

#### Special Colors

- **background:** Background color (usually darkest)
- **foreground:** Foreground/text color (usually brightest)
- **cursor:** Cursor color (usually an accent color)

#### Terminal Colors

- **colors:** List of exactly 16 Color objects
- **Order:** ANSI colors 0-15
  - 0-7: Normal colors (black, red, green, yellow, blue, magenta, cyan, white)
  - 8-15: Bright variants

#### Metadata

- **source_image:** Path to the image used for generation
- **backend:** Backend name (e.g., "pywal", "wallust", "custom")
- **generated_at:** Timestamp when scheme was generated
- **output_files:** Dictionary mapping format name to output file path (populated by OutputManager)

### Usage Examples

```python
# Create a color scheme
scheme = ColorScheme(
    background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
    foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
    cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
    colors=[
        Color(hex="#000000", rgb=(0, 0, 0)),    # color0
        Color(hex="#ff0000", rgb=(255, 0, 0)),  # color1
        # ... 14 more colors
    ],
    source_image=Path("~/wallpapers/mountain.png"),
    backend="pywal"
)

# Access colors
print(scheme.background.hex)  # '#1a1a1a'
print(scheme.colors[0].hex)   # '#000000' (color0)
print(scheme.backend)         # 'pywal'

# After OutputManager writes files
print(scheme.output_files)
# {'json': PosixPath('/home/user/.cache/colorscheme/colors.json'),
#  'css': PosixPath('/home/user/.cache/colorscheme/colors.css')}
```

### Validation

Pydantic validates:
- All special colors are Color objects
- Exactly 16 terminal colors
- source_image is a Path
- backend is a string
- generated_at is a datetime

```python
# Invalid - only 15 colors
scheme = ColorScheme(
    background=color,
    foreground=color,
    cursor=color,
    colors=[color] * 15,  # Only 15! Raises ValidationError
    source_image=Path("image.png"),
    backend="pywal"
)
```

---

## GeneratorConfig

**Location:** `colorscheme_generator.core.types`

Runtime configuration for color scheme generation.

### Class Definition

```python
class GeneratorConfig(BaseModel):
    """Runtime configuration for color scheme generation.

    Attributes:
        backend: Backend to use (overrides settings.generation.default_backend)
        color_count: Number of colors to extract
        saturation_adjustment: Saturation adjustment factor
        output_dir: Output directory (overrides settings.output.directory)
        formats: Output formats (overrides settings.output.formats)
        backend_options: Backend-specific options
    """
    # Color extraction settings (for backends)
    backend: Backend | None = None
    color_count: int | None = None
    saturation_adjustment: float | None = None

    # File output settings (for OutputManager)
    output_dir: Path | None = None
    formats: list[ColorFormat] | None = None

    # Backend-specific options
    backend_options: dict[str, Any] = Field(default_factory=dict)
```

### Attributes

#### Color Extraction Settings

- **backend:** Backend to use (overrides default from settings)
- **color_count:** Number of colors to extract (default: 16)
- **saturation_adjustment:** Saturation adjustment factor (default: 1.0)

#### File Output Settings

- **output_dir:** Output directory (overrides settings.output.directory)
- **formats:** List of output formats (overrides settings.output.formats)

#### Backend Options

- **backend_options:** Dictionary of backend-specific options

### Class Methods

#### from_settings()

```python
@classmethod
def from_settings(
    cls, settings: AppConfig, **overrides: Any
) -> "GeneratorConfig":
    """Create config from settings with optional overrides.

    Args:
        settings: AppConfig from settings.toml
        **overrides: Runtime overrides for any field

    Returns:
        GeneratorConfig with merged settings and overrides
    """
```

**Purpose:** Create GeneratorConfig by merging settings.toml defaults with runtime overrides.

**Example:**
```python
from colorscheme_generator.config.settings import Settings

config = GeneratorConfig.from_settings(
    Settings.get(),
    backend=Backend.WALLUST,
    output_dir=Path("/tmp/colors"),
    formats=[ColorFormat.JSON, ColorFormat.CSS]
)
```

#### get_backend_settings()

```python
def get_backend_settings(self, settings: AppConfig) -> dict[str, Any]:
    """Get backend-specific settings merged with runtime options.

    Args:
        settings: AppConfig from settings.toml

    Returns:
        Merged backend settings
    """
```

**Purpose:** Get backend-specific configuration merged with runtime options.

**Example:**
```python
config = GeneratorConfig(backend=Backend.PYWAL)
backend_settings = config.get_backend_settings(Settings.get())
print(backend_settings["cache_dir"])  # PosixPath('/home/user/.cache/wal')
```

### Usage Examples

```python
# Create with defaults from settings
config = GeneratorConfig.from_settings(Settings.get())

# Override specific settings
config = GeneratorConfig.from_settings(
    Settings.get(),
    backend=Backend.CUSTOM,
    color_count=32,
    output_dir=Path("~/.config/colors"),
    formats=[ColorFormat.JSON]
)

# With backend-specific options
config = GeneratorConfig.from_settings(
    Settings.get(),
    backend=Backend.CUSTOM,
    backend_options={
        "algorithm": "median_cut",
        "n_clusters": 24
    }
)

# Use in generation
generator = ColorSchemeGeneratorFactory.create(config.backend, settings)
scheme = generator.generate(image_path, config)
```

---

## Next Steps

- **[Backends API](backends.md)** - Backend implementations
- **[Managers API](managers.md)** - OutputManager
- **[Configuration API](configuration.md)** - Configuration system
- **[Exceptions API](exceptions.md)** - Exception hierarchy

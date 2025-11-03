# Backends API Reference

**Module:** `colorscheme_generator.backends`
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [PywalGenerator](#pywalgenerator)
2. [WallustGenerator](#wallustgenerator)
3. [CustomGenerator](#customgenerator)
4. [ColorSchemeGeneratorFactory](#colorscheme generatorfactory)

---

## PywalGenerator

**Location:** `colorscheme_generator.backends.pywal`

Backend that uses pywal for color extraction.

### Class Definition

```python
class PywalGenerator(ColorSchemeGenerator):
    """Pywal-based color scheme generator.

    Uses pywal library (if available) or wal CLI command to extract colors.
    Reads from ~/.cache/wal/colors.json after pywal generates colors.
    """
```

### Constructor

```python
def __init__(self, settings: AppConfig):
    """Initialize Pywal generator.

    Args:
        settings: Application configuration
    """
```

### Properties

#### backend_name

```python
@property
def backend_name(self) -> str:
    """Returns 'pywal'"""
```

### Methods

#### is_available()

```python
def is_available(self) -> bool:
    """Check if pywal is available.

    Checks:
    1. If use_library=True: Try to import pywal
    2. If use_library=False: Check if 'wal' command exists in PATH

    Returns:
        True if pywal is available, False otherwise
    """
```

#### generate()

```python
def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
    """Generate color scheme using pywal.

    Process:
    1. Validate image file exists
    2. Run pywal (library or CLI mode)
    3. Read colors from ~/.cache/wal/colors.json
    4. Parse and return ColorScheme

    Args:
        image_path: Path to source image
        config: Generation configuration

    Returns:
        ColorScheme with extracted colors

    Raises:
        InvalidImageError: If image doesn't exist or is invalid
        BackendNotAvailableError: If pywal is not available
        ColorExtractionError: If color extraction fails
    """
```

### Configuration

**Settings (settings.toml):**
```toml
[backends.pywal]
use_library = true  # Use pywal library vs CLI
cache_dir = "$HOME/.cache/wal"
```

### Usage Examples

```python
from colorscheme_generator.backends.pywal import PywalGenerator
from colorscheme_generator.config.settings import Settings

# Create generator
settings = Settings.get()
generator = PywalGenerator(settings)

# Check availability
if generator.is_available():
    # Generate colors
    scheme = generator.generate(
        Path("~/wallpapers/mountain.png"),
        GeneratorConfig()
    )
    print(scheme.background.hex)
```

### How It Works

**Library Mode (use_library=True):**
```python
import pywal
colors = pywal.colors.get(image_path)
# Parse colors into ColorScheme
```

**CLI Mode (use_library=False):**
```bash
wal -i /path/to/image.png
# Then read from ~/.cache/wal/colors.json
```

### Dependencies

- **Required:** None (pywal is optional)
- **Optional:** `pywal>=3.3.0` (install with `uv pip install -e ".[pywal]"`)
- **External:** `wal` command (if use_library=False)

---

## WallustGenerator

**Location:** `colorscheme_generator.backends.wallust`

Backend that uses wallust for color extraction.

### Class Definition

```python
class WallustGenerator(ColorSchemeGenerator):
    """Wallust-based color scheme generator.

    Uses wallust Rust binary to extract colors.
    Runs 'wallust --json' and parses JSON from stdout.
    """
```

### Constructor

```python
def __init__(self, settings: AppConfig):
    """Initialize Wallust generator.

    Args:
        settings: Application configuration
    """
```

### Properties

#### backend_name

```python
@property
def backend_name(self) -> str:
    """Returns 'wallust'"""
```

### Methods

#### is_available()

```python
def is_available(self) -> bool:
    """Check if wallust is available.

    Checks if 'wallust' command exists in PATH.

    Returns:
        True if wallust is available, False otherwise
    """
```

#### generate()

```python
def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
    """Generate color scheme using wallust.

    Process:
    1. Validate image file exists
    2. Run 'wallust --json <image>'
    3. Parse JSON from stdout
    4. Return ColorScheme

    Args:
        image_path: Path to source image
        config: Generation configuration

    Returns:
        ColorScheme with extracted colors

    Raises:
        InvalidImageError: If image doesn't exist or is invalid
        BackendNotAvailableError: If wallust is not available
        ColorExtractionError: If color extraction fails
    """
```

### Configuration

**Settings (settings.toml):**
```toml
[backends.wallust]
binary_path = "wallust"  # Path to wallust binary
```

### Usage Examples

```python
from colorscheme_generator.backends.wallust import WallustGenerator
from colorscheme_generator.config.settings import Settings

# Create generator
settings = Settings.get()
generator = WallustGenerator(settings)

# Check availability
if generator.is_available():
    # Generate colors
    scheme = generator.generate(
        Path("~/wallpapers/sunset.png"),
        GeneratorConfig()
    )
    print(scheme.colors[0].hex)
```

### How It Works

```bash
# Run wallust with JSON output
wallust --json /path/to/image.png

# Outputs JSON to stdout:
{
  "special": {
    "background": "#1a1a1a",
    "foreground": "#ffffff",
    "cursor": "#ff0000"
  },
  "colors": {
    "color0": "#000000",
    "color1": "#ff0000",
    ...
  }
}
```

### Dependencies

- **Required:** None
- **External:** `wallust` binary (install via `cargo install wallust`)

---

## CustomGenerator

**Location:** `colorscheme_generator.backends.custom`

Backend that uses PIL and scikit-learn for color extraction.

### Class Definition

```python
class CustomGenerator(ColorSchemeGenerator):
    """Custom Python-based color scheme generator.

    Uses PIL (Pillow) for image processing and scikit-learn for color clustering.
    Supports multiple algorithms: K-means, median cut, octree.
    """
```

### Constructor

```python
def __init__(self, settings: AppConfig):
    """Initialize Custom generator.

    Args:
        settings: Application configuration
    """
```

### Properties

#### backend_name

```python
@property
def backend_name(self) -> str:
    """Returns 'custom'"""
```

### Methods

#### is_available()

```python
def is_available(self) -> bool:
    """Check if custom backend is available.

    Always returns True since PIL and scikit-learn are required dependencies.

    Returns:
        True
    """
```

#### generate()

```python
def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
    """Generate color scheme using custom algorithm.

    Process:
    1. Load image with PIL
    2. Extract dominant colors using selected algorithm
    3. Assign colors to background/foreground/cursor
    4. Return ColorScheme

    Args:
        image_path: Path to source image
        config: Generation configuration

    Returns:
        ColorScheme with extracted colors

    Raises:
        InvalidImageError: If image cannot be loaded
        ColorExtractionError: If color extraction fails
    """
```

### Configuration

**Settings (settings.toml):**
```toml
[backends.custom]
algorithm = "kmeans"  # kmeans, median_cut, or octree
n_clusters = 16       # Number of colors to extract
saturation_boost = 1.2  # Saturation adjustment factor
```

### Algorithms

#### K-means Clustering

```python
config = GeneratorConfig(
    backend=Backend.CUSTOM,
    backend_options={"algorithm": "kmeans", "n_clusters": 16}
)
```

**How it works:**
1. Convert image to RGB array
2. Run K-means clustering to find dominant colors
3. Sort colors by luminance
4. Assign to color scheme

**Pros:** Fast, good color separation
**Cons:** May miss subtle colors

#### Median Cut

```python
config = GeneratorConfig(
    backend=Backend.CUSTOM,
    backend_options={"algorithm": "median_cut"}
)
```

**How it works:**
1. Recursively split color space at median
2. Extract representative colors from each bucket
3. Sort and assign to color scheme

**Pros:** Good color distribution
**Cons:** Slower than K-means

#### Octree

```python
config = GeneratorConfig(
    backend=Backend.CUSTOM,
    backend_options={"algorithm": "octree"}
)
```

**How it works:**
1. Build octree of color space
2. Reduce to desired number of colors
3. Extract and assign colors

**Pros:** Accurate color representation
**Cons:** Most computationally expensive

### Usage Examples

```python
from colorscheme_generator.backends.custom import CustomGenerator
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.config.enums import Backend

# Create generator
settings = Settings.get()
generator = CustomGenerator(settings)

# Generate with K-means
config = GeneratorConfig(
    backend=Backend.CUSTOM,
    backend_options={"algorithm": "kmeans", "n_clusters": 24}
)
scheme = generator.generate(Path("~/wallpapers/forest.png"), config)

# Generate with median cut
config = GeneratorConfig(
    backend=Backend.CUSTOM,
    backend_options={"algorithm": "median_cut"}
)
scheme = generator.generate(Path("~/wallpapers/ocean.png"), config)
```

### Dependencies

- **Required:** `pillow>=10.0.0`, `numpy>=1.24.0`, `scikit-learn>=1.3.0`
- **External:** None

---

## ColorSchemeGeneratorFactory

**Location:** `colorscheme_generator.factory`

Factory for creating backend instances.

### Class Definition

```python
class ColorSchemeGeneratorFactory:
    """Factory for creating ColorSchemeGenerator instances."""
```

### Static Methods

#### create()

```python
@staticmethod
def create(backend: Backend, settings: AppConfig) -> ColorSchemeGenerator:
    """Create a specific backend instance.

    Args:
        backend: Backend type to create
        settings: Application configuration

    Returns:
        ColorSchemeGenerator instance

    Raises:
        ValueError: If backend is unknown
    """
```

**Example:**
```python
from colorscheme_generator.factory import ColorSchemeGeneratorFactory
from colorscheme_generator.config.enums import Backend
from colorscheme_generator.config.settings import Settings

settings = Settings.get()
generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
```

#### create_auto()

```python
@staticmethod
def create_auto(settings: AppConfig) -> ColorSchemeGenerator:
    """Automatically detect and create best available backend.

    Detection order:
    1. Wallust (fastest, Rust-based)
    2. Pywal (popular, Python/CLI)
    3. Custom (always available, pure Python)

    Args:
        settings: Application configuration

    Returns:
        First available ColorSchemeGenerator instance

    Raises:
        BackendNotAvailableError: If no backends are available
    """
```

**Example:**
```python
# Auto-detect best backend
generator = ColorSchemeGeneratorFactory.create_auto(settings)
print(f"Using backend: {generator.backend_name}")
```

#### list_available()

```python
@staticmethod
def list_available(settings: AppConfig) -> list[str]:
    """List all available backends.

    Args:
        settings: Application configuration

    Returns:
        List of available backend names
    """
```

**Example:**
```python
available = ColorSchemeGeneratorFactory.list_available(settings)
print(f"Available backends: {', '.join(available)}")
# Output: "Available backends: wallust, pywal, custom"
```

---

## Next Steps

- **[Core API](core.md)** - Core abstractions and types
- **[Managers API](managers.md)** - OutputManager
- **[Usage Patterns](../guides/usage_patterns.md)** - Common usage patterns

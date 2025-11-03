# Configuration API Reference

**Module:** `colorscheme_generator.config`
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Settings](#settings)
2. [AppConfig](#appconfig)
3. [Enums](#enums)
4. [Defaults](#defaults)

---

## Settings

**Location:** `colorscheme_generator.config.settings`

Dynaconf-based settings loader with Pydantic validation.

### Class Definition

```python
class Settings:
    """Settings loader using Dynaconf + Pydantic validation.

    Loads from:
    1. defaults.py (default values)
    2. settings.toml (user configuration)
    3. Environment variables

    Validates with Pydantic (AppConfig model).
    """
```

### Class Methods

#### get()

```python
@classmethod
def get(cls) -> AppConfig:
    """Get validated application configuration.

    Process:
    1. Load settings.toml with Dynaconf
    2. Convert keys to lowercase
    3. Resolve environment variables ($HOME, etc.)
    4. Validate with Pydantic
    5. Return AppConfig instance

    Returns:
        Validated AppConfig instance

    Raises:
        ValidationError: If settings are invalid
    """
```

**Example:**
```python
from colorscheme_generator.config.settings import Settings

settings = Settings.get()
print(settings.output.directory)  # PosixPath('/home/user/.cache/colorscheme')
```

### Configuration File

**Location:** `cli/config/settings.toml` (or module-specific location)

**Example settings.toml:**
```toml
[output]
directory = "$HOME/.cache/colorscheme"
formats = ["json", "css", "sh"]

[generation]
default_backend = "pywal"
color_count = 16
saturation_adjustment = 1.0

[backends.pywal]
use_library = true
cache_dir = "$HOME/.cache/wal"

[backends.wallust]
binary_path = "wallust"

[backends.custom]
algorithm = "kmeans"
n_clusters = 16
saturation_boost = 1.2

[templates]
directory = "templates"
```

### Environment Variables

Dynaconf resolves environment variables in settings:

```toml
directory = "$HOME/.cache/colorscheme"  # Resolves to /home/user/.cache/colorscheme
```

---

## AppConfig

**Location:** `colorscheme_generator.config.config`

Pydantic model for application configuration.

### Class Definition

```python
class AppConfig(BaseModel):
    """Application configuration model.

    Attributes:
        output: Output settings
        generation: Generation settings
        backends: Backend-specific settings
        templates: Template settings
    """
    output: OutputSettings
    generation: GenerationSettings
    backends: BackendSettings
    templates: TemplateSettings
```

### Sub-Models

#### OutputSettings

```python
class OutputSettings(BaseModel):
    """Output file settings.

    Attributes:
        directory: Output directory path
        formats: List of output formats
    """
    directory: Path
    formats: list[ColorFormat]
```

**Example:**
```python
settings.output.directory  # PosixPath('/home/user/.cache/colorscheme')
settings.output.formats    # [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.SHELL]
```

#### GenerationSettings

```python
class GenerationSettings(BaseModel):
    """Color generation settings.

    Attributes:
        default_backend: Default backend to use
        color_count: Number of colors to extract
        saturation_adjustment: Saturation adjustment factor
    """
    default_backend: Backend
    color_count: int = Field(ge=1, le=256)
    saturation_adjustment: float = Field(ge=0.0, le=2.0)
```

**Example:**
```python
settings.generation.default_backend        # Backend.PYWAL
settings.generation.color_count            # 16
settings.generation.saturation_adjustment  # 1.0
```

#### BackendSettings

```python
class BackendSettings(BaseModel):
    """Backend-specific settings.

    Attributes:
        pywal: Pywal backend settings
        wallust: Wallust backend settings
        custom: Custom backend settings
    """
    pywal: PywalBackendSettings
    wallust: WallustBackendSettings
    custom: CustomBackendSettings
```

**PywalBackendSettings:**
```python
class PywalBackendSettings(BaseModel):
    use_library: bool = True
    cache_dir: Path = Path.home() / ".cache/wal"
```

**WallustBackendSettings:**
```python
class WallustBackendSettings(BaseModel):
    binary_path: str = "wallust"
```

**CustomBackendSettings:**
```python
class CustomBackendSettings(BaseModel):
    algorithm: ColorAlgorithm = ColorAlgorithm.KMEANS
    n_clusters: int = Field(16, ge=1, le=256)
    saturation_boost: float = Field(1.2, ge=0.0, le=2.0)
```

**Example:**
```python
settings.backends.pywal.use_library     # True
settings.backends.pywal.cache_dir       # PosixPath('/home/user/.cache/wal')
settings.backends.wallust.binary_path   # 'wallust'
settings.backends.custom.algorithm      # ColorAlgorithm.KMEANS
```

#### TemplateSettings

```python
class TemplateSettings(BaseModel):
    """Template system settings.

    Attributes:
        directory: Template directory path (relative to module root)
    """
    directory: str = "templates"
```

**Example:**
```python
settings.templates.directory  # 'templates'
```

---

## Enums

**Location:** `colorscheme_generator.config.enums`

### Backend

```python
class Backend(str, Enum):
    """Available color extraction backends."""
    PYWAL = "pywal"
    WALLUST = "wallust"
    CUSTOM = "custom"
```

**Usage:**
```python
from colorscheme_generator.config.enums import Backend

backend = Backend.PYWAL
print(backend.value)  # 'pywal'
```

### ColorFormat

```python
class ColorFormat(str, Enum):
    """Available output formats."""
    JSON = "json"
    CSS = "css"
    SHELL = "sh"
    YAML = "yaml"
```

**Usage:**
```python
from colorscheme_generator.config.enums import ColorFormat

formats = [ColorFormat.JSON, ColorFormat.CSS]
for fmt in formats:
    print(fmt.value)  # 'json', 'css'
```

### ColorAlgorithm

```python
class ColorAlgorithm(str, Enum):
    """Color extraction algorithms for custom backend."""
    KMEANS = "kmeans"
    MEDIAN_CUT = "median_cut"
    OCTREE = "octree"
```

**Usage:**
```python
from colorscheme_generator.config.enums import ColorAlgorithm

algorithm = ColorAlgorithm.KMEANS
print(algorithm.value)  # 'kmeans'
```

---

## Defaults

**Location:** `colorscheme_generator.config.defaults`

Default values for configuration.

### Constants

```python
# Output defaults
DEFAULT_OUTPUT_DIRECTORY = Path.home() / ".cache/colorscheme"
DEFAULT_OUTPUT_FORMATS = [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.SHELL]

# Generation defaults
DEFAULT_BACKEND = Backend.PYWAL
DEFAULT_COLOR_COUNT = 16
DEFAULT_SATURATION_ADJUSTMENT = 1.0

# Pywal backend defaults
PYWAL_USE_LIBRARY = True
PYWAL_CACHE_DIR = Path.home() / ".cache/wal"

# Wallust backend defaults
WALLUST_BINARY_PATH = "wallust"

# Custom backend defaults
CUSTOM_ALGORITHM = ColorAlgorithm.KMEANS
CUSTOM_N_CLUSTERS = 16
CUSTOM_SATURATION_BOOST = 1.2

# Template defaults
TEMPLATE_DIRECTORY = "templates"
```

**Usage:**
```python
from colorscheme_generator.config.defaults import (
    DEFAULT_OUTPUT_DIRECTORY,
    DEFAULT_BACKEND,
)

print(DEFAULT_OUTPUT_DIRECTORY)  # PosixPath('/home/user/.cache/colorscheme')
print(DEFAULT_BACKEND)           # Backend.PYWAL
```

---

## Configuration Hierarchy

### Loading Order

```
1. Defaults (defaults.py)
   ↓
2. Settings File (settings.toml)
   ↓
3. Environment Variables
   ↓
4. Pydantic Validation
   ↓
5. Runtime Overrides (GeneratorConfig)
```

### Example

**defaults.py:**
```python
DEFAULT_BACKEND = Backend.PYWAL
DEFAULT_COLOR_COUNT = 16
```

**settings.toml:**
```toml
[generation]
default_backend = "wallust"  # Overrides default
# color_count not specified, uses default (16)
```

**Runtime:**
```python
# Load settings (wallust, 16)
settings = Settings.get()

# Override at runtime
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.CUSTOM,  # Overrides settings
    color_count=24           # Overrides settings
)

# Final: Custom backend, 24 colors
```

---

## Validation

### Pydantic Validation

All configuration is validated with Pydantic:

```python
# Valid
config = AppConfig(
    output=OutputSettings(
        directory=Path("/tmp/colors"),
        formats=[ColorFormat.JSON]
    ),
    generation=GenerationSettings(
        default_backend=Backend.PYWAL,
        color_count=16,
        saturation_adjustment=1.0
    ),
    ...
)

# Invalid - raises ValidationError
config = AppConfig(
    output=OutputSettings(
        directory="/tmp/colors",  # Should be Path
        formats=["json"]          # Should be list[ColorFormat]
    ),
    ...
)
```

### Field Validation

```python
class GenerationSettings(BaseModel):
    color_count: int = Field(ge=1, le=256)  # Must be 1-256
    saturation_adjustment: float = Field(ge=0.0, le=2.0)  # Must be 0.0-2.0

# Valid
settings = GenerationSettings(
    default_backend=Backend.PYWAL,
    color_count=16,
    saturation_adjustment=1.2
)

# Invalid - raises ValidationError
settings = GenerationSettings(
    default_backend=Backend.PYWAL,
    color_count=300,  # Too high!
    saturation_adjustment=1.0
)
```

---

## Usage Examples

### Basic Configuration

```python
from colorscheme_generator.config.settings import Settings

# Load configuration
settings = Settings.get()

# Access settings
print(settings.output.directory)
print(settings.generation.default_backend)
print(settings.backends.pywal.cache_dir)
```

### Runtime Overrides

```python
from colorscheme_generator.core.types import GeneratorConfig
from colorscheme_generator.config.enums import Backend, ColorFormat

# Load base settings
settings = Settings.get()

# Create config with overrides
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.CUSTOM,
    output_dir=Path("/tmp/colors"),
    formats=[ColorFormat.JSON, ColorFormat.YAML],
    color_count=24
)
```

### Custom Settings File

```python
from dynaconf import Dynaconf
from colorscheme_generator.config.config import AppConfig

# Load from custom location
dynaconf = Dynaconf(
    settings_files=["my_custom_settings.toml"],
    lowercase_read=True,
)

# Validate
settings = AppConfig(**dynaconf.as_dict())
```

---

## Next Steps

- **[Core API](core.md)** - Core abstractions and types
- **[Getting Started](../guides/getting_started.md)** - Quick start guide
- **[Examples](../reference/examples.md)** - Configuration examples

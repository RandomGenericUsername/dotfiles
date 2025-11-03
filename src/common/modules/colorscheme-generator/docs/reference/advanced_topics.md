# Advanced Topics

**Module:** `colorscheme_generator`
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Security Considerations](#security-considerations)
2. [Performance Optimization](#performance-optimization)
3. [Extensibility](#extensibility)
4. [Testing Strategy](#testing-strategy)
5. [Deployment](#deployment)

---

## Security Considerations

### Input Validation

**Image Path Validation:**
```python
from pathlib import Path

def validate_image_path(image_path: Path) -> Path:
    """Validate image path for security."""
    # Resolve to absolute path
    image_path = image_path.expanduser().resolve()

    # Check if path exists
    if not image_path.exists():
        raise InvalidImageError(image_path, "File does not exist")

    # Check if it's a file (not directory)
    if not image_path.is_file():
        raise InvalidImageError(image_path, "Path is not a file")

    # Check file extension
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    if image_path.suffix.lower() not in allowed_extensions:
        raise InvalidImageError(image_path, f"Unsupported format: {image_path.suffix}")

    # Check file size (prevent DoS)
    max_size = 50 * 1024 * 1024  # 50MB
    if image_path.stat().st_size > max_size:
        raise InvalidImageError(image_path, "File too large")

    return image_path

# Usage
safe_path = validate_image_path(user_provided_path)
scheme = generator.generate(safe_path, config)
```

**Output Path Validation:**
```python
def validate_output_path(output_dir: Path) -> Path:
    """Validate output directory for security."""
    # Resolve to absolute path
    output_dir = output_dir.expanduser().resolve()

    # Prevent writing outside allowed directories
    allowed_bases = [
        Path.home() / ".cache",
        Path.home() / ".config",
        Path("/tmp"),
    ]

    if not any(output_dir.is_relative_to(base) for base in allowed_bases):
        raise ValueError(f"Output directory not allowed: {output_dir}")

    return output_dir
```

### Command Injection Prevention

**Safe Subprocess Execution:**
```python
import subprocess
from pathlib import Path

def safe_run_command(command: list[str], image_path: Path) -> subprocess.CompletedProcess:
    """Run command safely without shell injection."""
    # Never use shell=True
    # Always pass command as list
    # Validate all arguments

    validated_path = validate_image_path(image_path)

    # Use list, not string
    result = subprocess.run(
        [command[0], str(validated_path)],  # No shell expansion
        capture_output=True,
        text=True,
        timeout=30,  # Prevent hanging
        check=False
    )

    return result
```

### Dependency Security

**Pin Dependencies:**
```toml
# pyproject.toml
dependencies = [
    "pydantic>=2.11.9,<3.0.0",
    "pillow>=10.0.0,<11.0.0",
    "jinja2>=3.1.6,<4.0.0",
]
```

**Regular Updates:**
```bash
# Check for security updates
uv pip list --outdated

# Update dependencies
uv pip install --upgrade pydantic pillow jinja2
```

---

## Performance Optimization

### Image Preprocessing

**Resize Large Images:**
```python
from PIL import Image

def preprocess_image(image_path: Path, max_size=(1920, 1080)) -> Path:
    """Resize image for faster processing."""
    img = Image.open(image_path)

    # Only resize if larger than max_size
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save to temp file
        temp_path = Path("/tmp") / f"resized_{image_path.name}"
        img.save(temp_path, optimize=True)
        return temp_path

    return image_path

# Usage
preprocessed = preprocess_image(image_path)
scheme = generator.generate(preprocessed, config)
```

### Caching

**Cache Generated Schemes:**
```python
import hashlib
import json
from pathlib import Path

class SchemeCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, image_path: Path, backend: str) -> str:
        """Generate cache key from image hash and backend."""
        with open(image_path, "rb") as f:
            image_hash = hashlib.sha256(f.read()).hexdigest()
        return f"{backend}_{image_hash}"

    def get(self, image_path: Path, backend: str) -> ColorScheme | None:
        """Get cached scheme if available."""
        key = self.get_cache_key(image_path, backend)
        cache_file = self.cache_dir / f"{key}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
            return ColorScheme(**data)

        return None

    def set(self, image_path: Path, backend: str, scheme: ColorScheme):
        """Cache generated scheme."""
        key = self.get_cache_key(image_path, backend)
        cache_file = self.cache_dir / f"{key}.json"

        with open(cache_file, "w") as f:
            json.dump(scheme.model_dump(mode="json"), f)

# Usage
cache = SchemeCache(Path.home() / ".cache/colorscheme_cache")

cached = cache.get(image_path, generator.backend_name)
if cached:
    scheme = cached
else:
    scheme = generator.generate(image_path, config)
    cache.set(image_path, generator.backend_name, scheme)
```

### Parallel Processing

**Process Multiple Images:**
```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_images_parallel(images: list[Path], max_workers=4):
    """Process multiple images in parallel."""
    def process_one(image_path):
        settings = Settings.get()
        generator = ColorSchemeGeneratorFactory.create_auto(settings)
        config = GeneratorConfig.from_settings(settings)
        return generator.generate(image_path, config)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_one, img): img for img in images}

        results = {}
        for future in as_completed(futures):
            image = futures[future]
            try:
                scheme = future.result()
                results[image] = scheme
            except Exception as e:
                results[image] = e

        return results
```

---

## Extensibility

### Adding a New Backend

**Step 1: Implement ColorSchemeGenerator:**
```python
from colorscheme_generator.core.base import ColorSchemeGenerator
from colorscheme_generator.core.types import ColorScheme, GeneratorConfig

class MyCustomBackend(ColorSchemeGenerator):
    """Custom backend implementation."""

    def __init__(self, settings: AppConfig):
        self.settings = settings

    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
        """Extract colors using custom algorithm."""
        # Your implementation
        colors = self._extract_colors(image_path)

        return ColorScheme(
            background=colors[0],
            foreground=colors[15],
            cursor=colors[1],
            colors=colors,
            source_image=image_path,
            backend=self.backend_name,
        )

    def is_available(self) -> bool:
        """Check if backend is available."""
        # Check dependencies
        return True

    @property
    def backend_name(self) -> str:
        return "my_custom"

    def _extract_colors(self, image_path: Path) -> list[Color]:
        """Extract colors from image."""
        # Your color extraction logic
        pass
```

**Step 2: Register in Factory:**
```python
# factory.py
def create(backend: Backend, settings: AppConfig) -> ColorSchemeGenerator:
    if backend == Backend.MY_CUSTOM:
        return MyCustomBackend(settings)
    # ... existing backends
```

**Step 3: Add to Enum:**
```python
# config/enums.py
class Backend(str, Enum):
    PYWAL = "pywal"
    WALLUST = "wallust"
    CUSTOM = "custom"
    MY_CUSTOM = "my_custom"  # Add this
```

### Adding a New Output Format

**Step 1: Create Template:**
```jinja2
{# templates/colors.ini.j2 #}
; Generated by colorscheme_generator
; Source: {{ source_image }}

[colors]
background = {{ background.hex }}
foreground = {{ foreground.hex }}
cursor = {{ cursor.hex }}

{% for i in range(16) %}
color{{ i }} = {{ colors[i].hex }}
{% endfor %}
```

**Step 2: Add to Enum:**
```python
# config/enums.py
class ColorFormat(str, Enum):
    JSON = "json"
    CSS = "css"
    SHELL = "sh"
    YAML = "yaml"
    INI = "ini"  # Add this
```

**Step 3: Use It:**
```python
config = GeneratorConfig.from_settings(
    settings,
    formats=[ColorFormat.INI]
)
```

### Custom Color Algorithms

**Implement Custom Algorithm:**
```python
def extract_colors_custom(image_path: Path, n_colors=16) -> list[Color]:
    """Custom color extraction algorithm."""
    from PIL import Image
    import numpy as np

    # Load image
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img)

    # Your custom algorithm
    # Example: Extract most frequent colors
    pixels_flat = pixels.reshape(-1, 3)
    unique, counts = np.unique(pixels_flat, axis=0, return_counts=True)

    # Sort by frequency
    sorted_indices = np.argsort(counts)[::-1]
    top_colors = unique[sorted_indices[:n_colors]]

    # Convert to Color objects
    colors = []
    for rgb in top_colors:
        hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        colors.append(Color(hex=hex_color, rgb=tuple(rgb)))

    return colors
```

---

## Testing Strategy

### Unit Tests

**Test Backend:**
```python
import pytest
from pathlib import Path
from colorscheme_generator.backends.custom import CustomGenerator

def test_custom_generator_available():
    """Test custom generator is always available."""
    settings = Settings.get()
    generator = CustomGenerator(settings)
    assert generator.is_available() is True

def test_custom_generator_generate(tmp_path):
    """Test color generation."""
    # Create test image
    from PIL import Image
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    image_path = tmp_path / "test.png"
    img.save(image_path)

    # Generate colors
    settings = Settings.get()
    generator = CustomGenerator(settings)
    config = GeneratorConfig.from_settings(settings)

    scheme = generator.generate(image_path, config)

    # Assertions
    assert scheme.backend == "custom"
    assert len(scheme.colors) == 16
    assert scheme.source_image == image_path
```

**Test OutputManager:**
```python
def test_output_manager_write(tmp_path):
    """Test output file writing."""
    settings = Settings.get()
    manager = OutputManager(settings)

    # Create test scheme
    scheme = ColorScheme(
        background=Color(hex="#000000", rgb=(0, 0, 0)),
        foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
        cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
        colors=[Color(hex=f"#{i:02x}{i:02x}{i:02x}", rgb=(i, i, i)) for i in range(16)],
        source_image=Path("/test.png"),
        backend="test"
    )

    # Write outputs
    output_files = manager.write_outputs(
        scheme,
        tmp_path,
        [ColorFormat.JSON]
    )

    # Assertions
    assert "json" in output_files
    assert output_files["json"].exists()
```

### Integration Tests

**Test Complete Workflow:**
```python
def test_complete_workflow(tmp_path):
    """Test complete generation workflow."""
    # Create test image
    from PIL import Image
    img = Image.new("RGB", (100, 100), color=(100, 150, 200))
    image_path = tmp_path / "test.png"
    img.save(image_path)

    # Complete workflow
    settings = Settings.get()
    generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
    config = GeneratorConfig.from_settings(
        settings,
        output_dir=tmp_path / "output",
        formats=[ColorFormat.JSON, ColorFormat.CSS]
    )

    scheme = generator.generate(image_path, config)

    manager = OutputManager(settings)
    output_files = manager.write_outputs(
        scheme,
        config.output_dir,
        config.formats
    )

    # Assertions
    assert len(output_files) == 2
    assert all(path.exists() for path in output_files.values())
```

---

## Deployment

### Production Configuration

**settings.toml:**
```toml
[output]
directory = "/var/cache/colorscheme"
formats = ["json", "css"]

[generation]
default_backend = "custom"  # Most reliable
color_count = 16

[backends.custom]
algorithm = "kmeans"  # Fastest
n_clusters = 16
```

### Monitoring

**Add Logging:**
```python
import logging

logger = logging.getLogger("colorscheme_generator")
logger.setLevel(logging.INFO)

# Log generation
logger.info(f"Generating colors from {image_path}")
scheme = generator.generate(image_path, config)
logger.info(f"Generated scheme with backend {scheme.backend}")
```

### Error Reporting

**Sentry Integration:**
```python
import sentry_sdk

sentry_sdk.init(dsn="your-dsn")

try:
    scheme = generator.generate(image_path, config)
except ColorSchemeGeneratorError as e:
    sentry_sdk.capture_exception(e)
    raise
```

---

## Next Steps

- **[Examples](examples.md)** - Comprehensive code examples
- **[Troubleshooting](troubleshooting.md)** - Common issues
- **[API Reference](../api/)** - Detailed API documentation

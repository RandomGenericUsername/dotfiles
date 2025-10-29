# Usage Patterns

**Module:** `colorscheme_generator`  
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Backend Selection Patterns](#backend-selection-patterns)
2. [Configuration Patterns](#configuration-patterns)
3. [Error Handling Patterns](#error-handling-patterns)
4. [Output Management Patterns](#output-management-patterns)
5. [Integration Patterns](#integration-patterns)

---

## Backend Selection Patterns

### Pattern 1: Auto-Detection

**Use case:** Let the system choose the best available backend

```python
from colorscheme_generator.factory import ColorSchemeGeneratorFactory
from colorscheme_generator.config.settings import Settings

settings = Settings.get()
generator = ColorSchemeGeneratorFactory.create_auto(settings)
print(f"Using backend: {generator.backend_name}")
```

**Detection order:** Wallust → Pywal → Custom

### Pattern 2: Explicit Selection

**Use case:** Use a specific backend

```python
from colorscheme_generator.factory import ColorSchemeGeneratorFactory
from colorscheme_generator.config.enums import Backend

generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
generator.ensure_available()  # Raises if not available
```

### Pattern 3: Fallback Chain

**Use case:** Try preferred backend, fall back to alternatives

```python
from colorscheme_generator.core.exceptions import BackendNotAvailableError

backends_to_try = [Backend.WALLUST, Backend.PYWAL, Backend.CUSTOM]

for backend in backends_to_try:
    try:
        generator = ColorSchemeGeneratorFactory.create(backend, settings)
        generator.ensure_available()
        print(f"Using {backend.value}")
        break
    except BackendNotAvailableError:
        continue
```

### Pattern 4: User Choice with Validation

**Use case:** Let user choose backend, validate availability

```python
def get_generator(backend_name: str, settings):
    """Get generator with user-specified backend."""
    try:
        backend = Backend(backend_name)
    except ValueError:
        available = ColorSchemeGeneratorFactory.list_available(settings)
        raise ValueError(f"Unknown backend '{backend_name}'. Available: {available}")
    
    generator = ColorSchemeGeneratorFactory.create(backend, settings)
    generator.ensure_available()
    return generator

# Usage
generator = get_generator("pywal", settings)
```

---

## Configuration Patterns

### Pattern 1: Settings-Based Configuration

**Use case:** Use settings.toml defaults

```python
from colorscheme_generator.core.types import GeneratorConfig

config = GeneratorConfig.from_settings(settings)
# Uses all defaults from settings.toml
```

### Pattern 2: Selective Overrides

**Use case:** Override specific settings

```python
config = GeneratorConfig.from_settings(
    settings,
    output_dir=Path("/tmp/colors"),  # Override
    formats=[ColorFormat.JSON]       # Override
    # Other settings from settings.toml
)
```

### Pattern 3: Backend-Specific Options

**Use case:** Pass options to specific backend

```python
# For custom backend with K-means
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.CUSTOM,
    backend_options={
        "algorithm": "kmeans",
        "n_clusters": 24,
        "saturation_boost": 1.5
    }
)

# For custom backend with median cut
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.CUSTOM,
    backend_options={
        "algorithm": "median_cut"
    }
)
```

### Pattern 4: Per-Image Configuration

**Use case:** Different config for each image

```python
images = {
    "mountain.png": {
        "backend": Backend.PYWAL,
        "output_dir": Path("~/.config/colors/mountain")
    },
    "ocean.png": {
        "backend": Backend.WALLUST,
        "output_dir": Path("~/.config/colors/ocean")
    }
}

for image_name, options in images.items():
    config = GeneratorConfig.from_settings(settings, **options)
    scheme = generator.generate(Path(f"~/wallpapers/{image_name}"), config)
    # ...
```

---

## Error Handling Patterns

### Pattern 1: Catch-All Error Handler

**Use case:** Handle any module error

```python
from colorscheme_generator.core.exceptions import ColorSchemeGeneratorError

try:
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    scheme = generator.generate(image_path, config)
    output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
except ColorSchemeGeneratorError as e:
    print(f"Error: {e}")
    # Log, notify user, etc.
```

### Pattern 2: Specific Error Handling

**Use case:** Different handling for different errors

```python
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    InvalidImageError,
    ColorExtractionError,
)

try:
    generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
    scheme = generator.generate(image_path, config)
except BackendNotAvailableError:
    # Fall back to custom backend
    generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
    scheme = generator.generate(image_path, config)
except InvalidImageError as e:
    print(f"Invalid image: {e.image_path}")
    return None
except ColorExtractionError as e:
    print(f"Extraction failed: {e}")
    return None
```

### Pattern 3: Retry with Different Algorithm

**Use case:** Retry with different backend/algorithm on failure

```python
def generate_with_retry(image_path, settings):
    """Generate colors with automatic retry."""
    strategies = [
        (Backend.WALLUST, {}),
        (Backend.PYWAL, {}),
        (Backend.CUSTOM, {"algorithm": "kmeans"}),
        (Backend.CUSTOM, {"algorithm": "median_cut"}),
        (Backend.CUSTOM, {"algorithm": "octree"}),
    ]
    
    for backend, options in strategies:
        try:
            generator = ColorSchemeGeneratorFactory.create(backend, settings)
            config = GeneratorConfig.from_settings(
                settings,
                backend=backend,
                backend_options=options
            )
            return generator.generate(image_path, config)
        except (BackendNotAvailableError, ColorExtractionError):
            continue
    
    raise RuntimeError("All strategies failed")
```

### Pattern 4: Graceful Degradation

**Use case:** Continue with partial success

```python
def write_outputs_gracefully(scheme, output_dir, formats, manager):
    """Write outputs, continue on individual format failures."""
    output_files = {}
    errors = {}
    
    for fmt in formats:
        try:
            files = manager.write_outputs(scheme, output_dir, [fmt])
            output_files.update(files)
        except Exception as e:
            errors[fmt.value] = str(e)
    
    return output_files, errors

# Usage
output_files, errors = write_outputs_gracefully(
    scheme, output_dir, formats, manager
)
print(f"Success: {len(output_files)}, Errors: {len(errors)}")
```

---

## Output Management Patterns

### Pattern 1: Single Format Output

**Use case:** Generate only one format

```python
output_files = manager.write_outputs(
    scheme,
    Path("~/.config/colors"),
    [ColorFormat.JSON]
)
```

### Pattern 2: Multiple Formats

**Use case:** Generate multiple formats

```python
output_files = manager.write_outputs(
    scheme,
    Path("~/.config/colors"),
    [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.SHELL, ColorFormat.YAML]
)
```

### Pattern 3: Organized Output Structure

**Use case:** Organize outputs by image/backend

```python
from pathlib import Path

def organize_outputs(scheme, base_dir, formats, manager):
    """Organize outputs in structured directory."""
    # Create directory: base_dir/backend/image_name/
    image_name = scheme.source_image.stem
    output_dir = base_dir / scheme.backend / image_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return manager.write_outputs(scheme, output_dir, formats)

# Usage
output_files = organize_outputs(
    scheme,
    Path("~/.cache/colorschemes"),
    [ColorFormat.JSON, ColorFormat.CSS],
    manager
)
# Result: ~/.cache/colorschemes/pywal/mountain/colors.json
#         ~/.cache/colorschemes/pywal/mountain/colors.css
```

### Pattern 4: Timestamped Outputs

**Use case:** Keep history of generated schemes

```python
from datetime import datetime

def write_timestamped_outputs(scheme, base_dir, formats, manager):
    """Write outputs with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = base_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return manager.write_outputs(scheme, output_dir, formats)

# Usage
output_files = write_timestamped_outputs(
    scheme,
    Path("~/.cache/colorscheme_history"),
    [ColorFormat.JSON],
    manager
)
# Result: ~/.cache/colorscheme_history/20251018_103000/colors.json
```

---

## Integration Patterns

### Pattern 1: Wallpaper Change Hook

**Use case:** Generate colors when wallpaper changes

```python
def on_wallpaper_change(wallpaper_path: Path):
    """Hook for wallpaper change events."""
    settings = Settings.get()
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    config = GeneratorConfig.from_settings(settings)
    
    try:
        scheme = generator.generate(wallpaper_path, config)
        manager = OutputManager(settings)
        output_files = manager.write_outputs(
            scheme,
            config.output_dir,
            config.formats
        )
        
        # Reload applications
        reload_applications(output_files)
        
        return scheme
    except ColorSchemeGeneratorError as e:
        print(f"Failed to generate colors: {e}")
        return None

def reload_applications(output_files):
    """Reload applications with new colors."""
    # Reload terminal, editor, etc.
    pass
```

### Pattern 2: CLI Integration

**Use case:** Integrate with command-line tools

```python
import argparse
from pathlib import Path

def cli_main():
    parser = argparse.ArgumentParser(description="Generate color schemes")
    parser.add_argument("image", type=Path, help="Source image")
    parser.add_argument("--backend", choices=["pywal", "wallust", "custom"])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--formats", nargs="+", choices=["json", "css", "sh", "yaml"])
    
    args = parser.parse_args()
    
    settings = Settings.get()
    
    # Create generator
    if args.backend:
        backend = Backend(args.backend)
        generator = ColorSchemeGeneratorFactory.create(backend, settings)
    else:
        generator = ColorSchemeGeneratorFactory.create_auto(settings)
    
    # Create config
    config_kwargs = {}
    if args.output_dir:
        config_kwargs["output_dir"] = args.output_dir
    if args.formats:
        config_kwargs["formats"] = [ColorFormat(f) for f in args.formats]
    
    config = GeneratorConfig.from_settings(settings, **config_kwargs)
    
    # Generate
    scheme = generator.generate(args.image, config)
    manager = OutputManager(settings)
    output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
    
    print(f"Generated {len(output_files)} files")
```

### Pattern 3: Batch Processing

**Use case:** Process multiple images

```python
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def process_image(image_path, generator, manager, settings):
    """Process single image."""
    config = GeneratorConfig.from_settings(
        settings,
        output_dir=Path(f"~/.cache/colorschemes/{image_path.stem}")
    )
    
    try:
        scheme = generator.generate(image_path, config)
        output_files = manager.write_outputs(
            scheme,
            config.output_dir,
            config.formats
        )
        return image_path, output_files, None
    except Exception as e:
        return image_path, None, str(e)

def batch_process(image_dir: Path, settings):
    """Process all images in directory."""
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    manager = OutputManager(settings)
    
    images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg"))
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(
            lambda img: process_image(img, generator, manager, settings),
            images
        )
    
    for image_path, output_files, error in results:
        if error:
            print(f"Failed {image_path.name}: {error}")
        else:
            print(f"Processed {image_path.name}: {len(output_files)} files")
```

### Pattern 4: Configuration File Generation

**Use case:** Generate config files for applications

```python
def generate_app_configs(scheme, app_config_dir: Path):
    """Generate application-specific config files."""
    # Alacritty config
    alacritty_config = f"""
colors:
  primary:
    background: '{scheme.background.hex}'
    foreground: '{scheme.foreground.hex}'
  cursor:
    text: '{scheme.background.hex}'
    cursor: '{scheme.cursor.hex}'
  normal:
    black:   '{scheme.colors[0].hex}'
    red:     '{scheme.colors[1].hex}'
    green:   '{scheme.colors[2].hex}'
    yellow:  '{scheme.colors[3].hex}'
    blue:    '{scheme.colors[4].hex}'
    magenta: '{scheme.colors[5].hex}'
    cyan:    '{scheme.colors[6].hex}'
    white:   '{scheme.colors[7].hex}'
  bright:
    black:   '{scheme.colors[8].hex}'
    red:     '{scheme.colors[9].hex}'
    green:   '{scheme.colors[10].hex}'
    yellow:  '{scheme.colors[11].hex}'
    blue:    '{scheme.colors[12].hex}'
    magenta: '{scheme.colors[13].hex}'
    cyan:    '{scheme.colors[14].hex}'
    white:   '{scheme.colors[15].hex}'
"""
    
    (app_config_dir / "alacritty_colors.yml").write_text(alacritty_config)
    
    # Add more application configs...
```

---

## Next Steps

- **[Integration Guide](integration.md)** - Detailed integration examples
- **[Templates Guide](templates.md)** - Working with templates
- **[Examples](../reference/examples.md)** - Comprehensive examples


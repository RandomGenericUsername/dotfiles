# Comprehensive Examples

**Module:** `colorscheme_generator`  
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Backend Examples](#backend-examples)
3. [Configuration Examples](#configuration-examples)
4. [Output Examples](#output-examples)
5. [Integration Examples](#integration-examples)
6. [Advanced Examples](#advanced-examples)

---

## Basic Examples

### Example 1: Simplest Usage

```python
from pathlib import Path
from colorscheme_generator import (
    ColorSchemeGeneratorFactory,
    OutputManager,
    Settings,
    GeneratorConfig,
)

# Load settings
settings = Settings.get()

# Auto-detect backend
generator = ColorSchemeGeneratorFactory.create_auto(settings)

# Create config from settings
config = GeneratorConfig.from_settings(settings)

# Generate colors
scheme = generator.generate(
    Path("~/wallpapers/mountain.png").expanduser(),
    config
)

# Write outputs
manager = OutputManager(settings)
output_files = manager.write_outputs(
    scheme,
    config.output_dir,
    config.formats
)

print(f"Generated {len(output_files)} files")
```

### Example 2: With Error Handling

```python
from colorscheme_generator.core.exceptions import ColorSchemeGeneratorError

try:
    settings = Settings.get()
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    config = GeneratorConfig.from_settings(settings)
    
    scheme = generator.generate(
        Path("~/wallpapers/sunset.png").expanduser(),
        config
    )
    
    manager = OutputManager(settings)
    output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
    
    print(f"Success! Background: {scheme.background.hex}")
except ColorSchemeGeneratorError as e:
    print(f"Error: {e}")
```

### Example 3: Inspect Generated Colors

```python
scheme = generator.generate(image_path, config)

print(f"Backend: {scheme.backend}")
print(f"Source: {scheme.source_image}")
print(f"Generated: {scheme.generated_at}")
print()
print(f"Background: {scheme.background.hex} RGB{scheme.background.rgb}")
print(f"Foreground: {scheme.foreground.hex} RGB{scheme.foreground.rgb}")
print(f"Cursor: {scheme.cursor.hex} RGB{scheme.cursor.rgb}")
print()
print("Terminal Colors:")
for i, color in enumerate(scheme.colors):
    print(f"  Color {i:2d}: {color.hex} RGB{color.rgb}")
```

---

## Backend Examples

### Example 4: Use Specific Backend

```python
from colorscheme_generator.config.enums import Backend

# Use Pywal
generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
scheme = generator.generate(image_path, config)

# Use Wallust
generator = ColorSchemeGeneratorFactory.create(Backend.WALLUST, settings)
scheme = generator.generate(image_path, config)

# Use Custom
generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
scheme = generator.generate(image_path, config)
```

### Example 5: Backend Fallback Chain

```python
from colorscheme_generator.core.exceptions import BackendNotAvailableError

backends = [Backend.WALLUST, Backend.PYWAL, Backend.CUSTOM]

for backend in backends:
    try:
        generator = ColorSchemeGeneratorFactory.create(backend, settings)
        generator.ensure_available()
        print(f"Using {backend.value}")
        break
    except BackendNotAvailableError:
        print(f"{backend.value} not available, trying next...")
        continue

scheme = generator.generate(image_path, config)
```

### Example 6: List Available Backends

```python
available = ColorSchemeGeneratorFactory.list_available(settings)
print(f"Available backends: {', '.join(available)}")

# Check each backend
for backend in [Backend.PYWAL, Backend.WALLUST, Backend.CUSTOM]:
    gen = ColorSchemeGeneratorFactory.create(backend, settings)
    status = "✓" if gen.is_available() else "✗"
    print(f"{status} {backend.value}")
```

### Example 7: Custom Backend with Different Algorithms

```python
algorithms = ["kmeans", "median_cut", "octree"]

for algo in algorithms:
    config = GeneratorConfig.from_settings(
        settings,
        backend=Backend.CUSTOM,
        backend_options={"algorithm": algo}
    )
    
    generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
    scheme = generator.generate(image_path, config)
    
    print(f"{algo}: Background={scheme.background.hex}")
```

---

## Configuration Examples

### Example 8: Override Output Directory

```python
config = GeneratorConfig.from_settings(
    settings,
    output_dir=Path("/tmp/my-colors")
)

scheme = generator.generate(image_path, config)
manager = OutputManager(settings)
output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
```

### Example 9: Override Output Formats

```python
from colorscheme_generator.config.enums import ColorFormat

config = GeneratorConfig.from_settings(
    settings,
    formats=[ColorFormat.JSON, ColorFormat.CSS]
)

output_files = manager.write_outputs(scheme, config.output_dir, config.formats)
```

### Example 10: Complete Configuration Override

```python
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.CUSTOM,
    output_dir=Path("~/.config/colors").expanduser(),
    formats=[ColorFormat.JSON, ColorFormat.YAML],
    color_count=24,
    saturation_adjustment=1.5,
    backend_options={
        "algorithm": "median_cut",
        "saturation_boost": 1.3
    }
)
```

---

## Output Examples

### Example 11: Write Single Format

```python
output_files = manager.write_outputs(
    scheme,
    Path("~/.config/colors").expanduser(),
    [ColorFormat.JSON]
)

print(f"JSON file: {output_files['json']}")
```

### Example 12: Write Multiple Formats

```python
output_files = manager.write_outputs(
    scheme,
    Path("~/.config/colors").expanduser(),
    [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.SHELL, ColorFormat.YAML]
)

for fmt, path in output_files.items():
    print(f"{fmt}: {path}")
```

### Example 13: Organized Output Structure

```python
def write_organized_outputs(scheme, base_dir, formats, manager):
    """Organize outputs by backend and image name."""
    output_dir = base_dir / scheme.backend / scheme.source_image.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    return manager.write_outputs(scheme, output_dir, formats)

output_files = write_organized_outputs(
    scheme,
    Path("~/.cache/colorschemes").expanduser(),
    [ColorFormat.JSON, ColorFormat.CSS],
    manager
)
# Result: ~/.cache/colorschemes/pywal/mountain/colors.json
```

### Example 14: Read Generated JSON

```python
import json

output_files = manager.write_outputs(
    scheme,
    output_dir,
    [ColorFormat.JSON]
)

# Read the JSON file
with open(output_files['json']) as f:
    data = json.load(f)

print(f"Background: {data['special']['background']}")
print(f"Color 0: {data['colors']['color0']}")
```

---

## Integration Examples

### Example 15: Wallpaper Change Hook

```python
def on_wallpaper_change(wallpaper_path: Path):
    """Generate colors when wallpaper changes."""
    settings = Settings.get()
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    config = GeneratorConfig.from_settings(settings)
    
    scheme = generator.generate(wallpaper_path, config)
    
    manager = OutputManager(settings)
    output_files = manager.write_outputs(
        scheme,
        config.output_dir,
        config.formats
    )
    
    # Reload applications
    reload_terminal()
    reload_window_manager()
    
    return scheme

# Usage
scheme = on_wallpaper_change(Path("~/wallpapers/new.png").expanduser())
```

### Example 16: Generate Application Configs

```python
def generate_alacritty_config(scheme, output_path):
    """Generate Alacritty color configuration."""
    config = f"""
[colors.primary]
background = '{scheme.background.hex}'
foreground = '{scheme.foreground.hex}'

[colors.normal]
black   = '{scheme.colors[0].hex}'
red     = '{scheme.colors[1].hex}'
green   = '{scheme.colors[2].hex}'
yellow  = '{scheme.colors[3].hex}'
blue    = '{scheme.colors[4].hex}'
magenta = '{scheme.colors[5].hex}'
cyan    = '{scheme.colors[6].hex}'
white   = '{scheme.colors[7].hex}'
"""
    output_path.write_text(config)

# Usage
generate_alacritty_config(
    scheme,
    Path("~/.config/alacritty/colors.toml").expanduser()
)
```

### Example 17: Batch Processing

```python
from pathlib import Path

def batch_process_images(image_dir: Path, settings):
    """Process all images in directory."""
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    manager = OutputManager(settings)
    
    images = list(image_dir.glob("*.png")) + list(image_dir.glob("*.jpg"))
    results = []
    
    for image in images:
        try:
            config = GeneratorConfig.from_settings(
                settings,
                output_dir=Path(f"~/.cache/colorschemes/{image.stem}").expanduser()
            )
            
            scheme = generator.generate(image, config)
            output_files = manager.write_outputs(
                scheme,
                config.output_dir,
                config.formats
            )
            
            results.append((image.name, "success", len(output_files)))
        except Exception as e:
            results.append((image.name, "error", str(e)))
    
    return results

# Usage
results = batch_process_images(
    Path("~/wallpapers").expanduser(),
    settings
)

for name, status, info in results:
    print(f"{name}: {status} - {info}")
```

---

## Advanced Examples

### Example 18: Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def process_single_image(image_path):
    """Process single image (for parallel execution)."""
    settings = Settings.get()
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    config = GeneratorConfig.from_settings(settings)
    
    scheme = generator.generate(image_path, config)
    
    manager = OutputManager(settings)
    output_files = manager.write_outputs(
        scheme,
        config.output_dir,
        config.formats
    )
    
    return image_path.name, len(output_files)

# Parallel processing
images = list(Path("~/wallpapers").expanduser().glob("*.png"))

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_single_image, images))

for name, count in results:
    print(f"{name}: {count} files")
```

### Example 19: Custom Color Adjustment

```python
def adjust_colors(scheme, saturation_factor=1.2, brightness_factor=1.1):
    """Adjust colors in scheme."""
    import colorsys
    
    def adjust_color(color):
        # Convert to HSL
        r, g, b = [x / 255.0 for x in color.rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        
        # Adjust
        s = min(1.0, s * saturation_factor)
        l = min(1.0, l * brightness_factor)
        
        # Convert back
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        rgb = tuple(int(x * 255) for x in (r, g, b))
        hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        return Color(hex=hex_color, rgb=rgb)
    
    # Adjust all colors
    scheme.background = adjust_color(scheme.background)
    scheme.foreground = adjust_color(scheme.foreground)
    scheme.cursor = adjust_color(scheme.cursor)
    scheme.colors = [adjust_color(c) for c in scheme.colors]
    
    return scheme

# Usage
scheme = generator.generate(image_path, config)
scheme = adjust_colors(scheme, saturation_factor=1.3)
```

### Example 20: Compare Backends

```python
def compare_backends(image_path, settings):
    """Compare color schemes from different backends."""
    backends = [Backend.PYWAL, Backend.WALLUST, Backend.CUSTOM]
    results = {}
    
    for backend in backends:
        try:
            generator = ColorSchemeGeneratorFactory.create(backend, settings)
            if not generator.is_available():
                continue
            
            config = GeneratorConfig.from_settings(settings)
            scheme = generator.generate(image_path, config)
            
            results[backend.value] = {
                "background": scheme.background.hex,
                "foreground": scheme.foreground.hex,
                "colors": [c.hex for c in scheme.colors]
            }
        except Exception as e:
            results[backend.value] = {"error": str(e)}
    
    return results

# Usage
comparison = compare_backends(
    Path("~/wallpapers/mountain.png").expanduser(),
    settings
)

for backend, data in comparison.items():
    print(f"\n{backend}:")
    if "error" in data:
        print(f"  Error: {data['error']}")
    else:
        print(f"  Background: {data['background']}")
        print(f"  Foreground: {data['foreground']}")
```

---

## Next Steps

- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Advanced Topics](advanced_topics.md)** - Advanced usage
- **[API Reference](../api/)** - Detailed API documentation


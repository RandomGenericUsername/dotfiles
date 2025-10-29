# Troubleshooting Guide

**Module:** `colorscheme_generator`  
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Backend Issues](#backend-issues)
3. [Color Extraction Issues](#color-extraction-issues)
4. [Output Generation Issues](#output-generation-issues)
5. [Configuration Issues](#configuration-issues)
6. [Performance Issues](#performance-issues)

---

## Installation Issues

### Issue 1: Module Not Found

**Symptom:**
```python
ModuleNotFoundError: No module named 'colorscheme_generator'
```

**Cause:** Module not installed or wrong virtual environment

**Solution:**
```bash
# Ensure you're in the correct directory
cd src/dotfiles/modules/colorscheme_generator

# Activate virtual environment
source .venv/bin/activate  # or: uv venv && source .venv/bin/activate

# Install module
uv pip install -e .
```

### Issue 2: Import Errors for Dependencies

**Symptom:**
```python
ModuleNotFoundError: No module named 'PIL'
ModuleNotFoundError: No module named 'sklearn'
```

**Cause:** Dependencies not installed

**Solution:**
```bash
# Install all dependencies
uv sync

# Or manually
uv pip install pillow numpy scikit-learn jinja2 pydantic dynaconf
```

### Issue 3: Pywal Backend Not Available

**Symptom:**
```python
BackendNotAvailableError: Backend 'pywal' is not available
```

**Cause:** Pywal not installed

**Solution:**
```bash
# Install pywal as optional dependency
uv pip install -e ".[pywal]"

# Or install pywal separately
pip install pywal
```

---

## Backend Issues

### Issue 1: Wallust Not Found

**Symptom:**
```python
BackendNotAvailableError: Backend 'wallust' is not available
```

**Cause:** Wallust binary not in PATH

**Solution:**
```bash
# Install wallust
cargo install wallust

# Verify installation
which wallust

# Or specify custom path in settings.toml
[backends.wallust]
binary_path = "/path/to/wallust"
```

### Issue 2: Pywal Cache Not Found

**Symptom:**
```python
ColorExtractionError: Failed to read pywal cache
```

**Cause:** Pywal hasn't been run yet or cache directory doesn't exist

**Solution:**
```bash
# Run pywal manually first
wal -i /path/to/image.png

# Or use library mode instead
[backends.pywal]
use_library = true  # in settings.toml
```

### Issue 3: Custom Backend Fails

**Symptom:**
```python
ColorExtractionError: K-means clustering failed
```

**Cause:** Image has too few colors or algorithm doesn't converge

**Solution:**
```python
# Try different algorithm
config = GeneratorConfig.from_settings(
    settings,
    backend=Backend.CUSTOM,
    backend_options={"algorithm": "median_cut"}  # Instead of kmeans
)

# Or reduce number of clusters
config = GeneratorConfig.from_settings(
    settings,
    backend_options={"n_clusters": 8}  # Instead of 16
)
```

---

## Color Extraction Issues

### Issue 1: Invalid Image Error

**Symptom:**
```python
InvalidImageError: Invalid image file: /path/to/image.png
```

**Cause:** Image file doesn't exist, is corrupt, or unsupported format

**Solution:**
```python
from pathlib import Path

# Check if file exists
image_path = Path("~/wallpapers/image.png").expanduser()
if not image_path.exists():
    print(f"Image not found: {image_path}")

# Check if file is readable
try:
    from PIL import Image
    img = Image.open(image_path)
    print(f"Image format: {img.format}, Size: {img.size}")
except Exception as e:
    print(f"Cannot open image: {e}")
```

### Issue 2: Poor Color Quality

**Symptom:** Generated colors don't match image well

**Cause:** Wrong backend or algorithm for image type

**Solution:**
```python
# Try different backends
backends_to_try = [Backend.WALLUST, Backend.PYWAL, Backend.CUSTOM]

for backend in backends_to_try:
    try:
        generator = ColorSchemeGeneratorFactory.create(backend, settings)
        scheme = generator.generate(image_path, config)
        # Evaluate quality
        break
    except Exception:
        continue

# Or try different custom algorithms
algorithms = ["kmeans", "median_cut", "octree"]

for algo in algorithms:
    config = GeneratorConfig.from_settings(
        settings,
        backend_options={"algorithm": algo}
    )
    scheme = generator.generate(image_path, config)
    # Compare results
```

### Issue 3: Colors Too Similar

**Symptom:** All generated colors are very similar

**Cause:** Image has low color variance or saturation too low

**Solution:**
```python
# Increase saturation adjustment
config = GeneratorConfig.from_settings(
    settings,
    saturation_adjustment=1.5,  # Boost saturation
    backend_options={"saturation_boost": 1.5}
)

# Or extract more colors and filter
config = GeneratorConfig.from_settings(
    settings,
    color_count=32,  # Extract more, use best 16
)
```

---

## Output Generation Issues

### Issue 1: Template Not Found

**Symptom:**
```python
TemplateRenderError: Failed to render template 'colors.toml.j2'
jinja2.exceptions.TemplateNotFound: colors.toml.j2
```

**Cause:** Template file doesn't exist

**Solution:**
```bash
# Check template directory
ls colorscheme_generator/templates/

# Create missing template
touch colorscheme_generator/templates/colors.toml.j2

# Or use existing formats
config = GeneratorConfig.from_settings(
    settings,
    formats=[ColorFormat.JSON, ColorFormat.CSS]  # Known formats
)
```

### Issue 2: Permission Denied

**Symptom:**
```python
OutputWriteError: Failed to write output file '/root/colors/colors.json'
PermissionError: [Errno 13] Permission denied
```

**Cause:** No write permission to output directory

**Solution:**
```python
# Use writable directory
config = GeneratorConfig.from_settings(
    settings,
    output_dir=Path.home() / ".cache/colorscheme"  # User directory
)

# Or create directory with correct permissions
output_dir = Path("/tmp/colors")
output_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
```

### Issue 3: Disk Full

**Symptom:**
```python
OutputWriteError: Failed to write output file
OSError: [Errno 28] No space left on device
```

**Cause:** Disk is full

**Solution:**
```bash
# Check disk space
df -h

# Clean up old files
rm -rf ~/.cache/colorscheme/old/*

# Use different partition
config = GeneratorConfig.from_settings(
    settings,
    output_dir=Path("/mnt/other/colors")
)
```

---

## Configuration Issues

### Issue 1: Settings File Not Found

**Symptom:**
```python
FileNotFoundError: settings.toml not found
```

**Cause:** Settings file doesn't exist or wrong location

**Solution:**
```bash
# Create settings file
mkdir -p cli/config
touch cli/config/settings.toml

# Add basic configuration
cat > cli/config/settings.toml << EOF
[output]
directory = "$HOME/.cache/colorscheme"
formats = ["json", "css"]

[generation]
default_backend = "custom"
EOF
```

### Issue 2: Invalid Configuration

**Symptom:**
```python
ValidationError: 1 validation error for AppConfig
```

**Cause:** Invalid values in settings.toml

**Solution:**
```toml
# Check types and values
[generation]
color_count = 16  # Must be integer 1-256
saturation_adjustment = 1.0  # Must be float 0.0-2.0

[output]
formats = ["json", "css"]  # Must be list of valid formats
```

### Issue 3: Environment Variables Not Resolved

**Symptom:** `$HOME` appears literally in paths

**Cause:** Dynaconf not resolving environment variables

**Solution:**
```python
# Ensure Settings.get() is used (not direct Dynaconf)
from colorscheme_generator.config.settings import Settings

settings = Settings.get()  # Resolves env vars
print(settings.output.directory)  # PosixPath('/home/user/...')
```

---

## Performance Issues

### Issue 1: Slow Color Extraction

**Symptom:** Generation takes > 10 seconds

**Cause:** Large image or slow algorithm

**Solution:**
```python
# Use faster backend
generator = ColorSchemeGeneratorFactory.create(Backend.WALLUST, settings)

# Or resize image first
from PIL import Image

img = Image.open(image_path)
img.thumbnail((800, 600))  # Resize
img.save("/tmp/resized.png")

scheme = generator.generate(Path("/tmp/resized.png"), config)
```

### Issue 2: High Memory Usage

**Symptom:** Process uses > 1GB RAM

**Cause:** Large image loaded into memory

**Solution:**
```python
# Resize image before processing
from PIL import Image

def resize_image(image_path, max_size=(1920, 1080)):
    img = Image.open(image_path)
    img.thumbnail(max_size)
    temp_path = Path("/tmp/resized.png")
    img.save(temp_path)
    return temp_path

resized = resize_image(image_path)
scheme = generator.generate(resized, config)
```

### Issue 3: Batch Processing Too Slow

**Symptom:** Processing 100 images takes hours

**Cause:** Sequential processing

**Solution:**
```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def process_image(image_path):
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    config = GeneratorConfig.from_settings(settings)
    return generator.generate(image_path, config)

# Parallel processing
images = list(Path("~/wallpapers").glob("*.png"))

with ProcessPoolExecutor(max_workers=4) as executor:
    schemes = list(executor.map(process_image, images))

print(f"Processed {len(schemes)} images")
```

---

## Common Error Messages

### "Backend 'X' is not available"

**Meaning:** Backend dependencies not installed  
**Fix:** Install backend (see [Backend Issues](#backend-issues))

### "Failed to extract colors from X using Y"

**Meaning:** Color extraction failed  
**Fix:** Try different backend or algorithm (see [Color Extraction Issues](#color-extraction-issues))

### "Failed to render template 'X'"

**Meaning:** Template error or not found  
**Fix:** Check template exists and syntax (see [Output Generation Issues](#output-generation-issues))

### "Failed to write output file 'X'"

**Meaning:** File write error  
**Fix:** Check permissions and disk space (see [Output Generation Issues](#output-generation-issues))

### "Invalid image file: X"

**Meaning:** Image cannot be read  
**Fix:** Check file exists and is valid image (see [Color Extraction Issues](#color-extraction-issues))

---

## Getting Help

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("colorscheme_generator")
logger.setLevel(logging.DEBUG)

# Now run your code
scheme = generator.generate(image_path, config)
```

### Check Backend Availability

```python
from colorscheme_generator.factory import ColorSchemeGeneratorFactory

available = ColorSchemeGeneratorFactory.list_available(settings)
print(f"Available backends: {available}")

for backend in [Backend.PYWAL, Backend.WALLUST, Backend.CUSTOM]:
    gen = ColorSchemeGeneratorFactory.create(backend, settings)
    print(f"{backend.value}: {gen.is_available()}")
```

### Validate Configuration

```python
from colorscheme_generator.config.settings import Settings

try:
    settings = Settings.get()
    print("Configuration valid!")
    print(f"Output dir: {settings.output.directory}")
    print(f"Formats: {settings.output.formats}")
except Exception as e:
    print(f"Configuration error: {e}")
```

---

## Next Steps

- **[Examples](examples.md)** - Comprehensive code examples
- **[Advanced Topics](advanced_topics.md)** - Advanced usage
- **[API Reference](../api/)** - Detailed API documentation


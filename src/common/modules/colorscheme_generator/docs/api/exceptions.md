# Exceptions API Reference

**Module:** `colorscheme_generator.core.exceptions`  
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Exception Hierarchy](#exception-hierarchy)
2. [ColorSchemeGeneratorError](#colorscheme generatorerror)
3. [BackendNotAvailableError](#backendnotavailableerror)
4. [ColorExtractionError](#colorextractionerror)
5. [TemplateRenderError](#templaterendererror)
6. [OutputWriteError](#outputwriteerror)
7. [InvalidImageError](#invalidimageerror)
8. [Error Handling Patterns](#error-handling-patterns)

---

## Exception Hierarchy

```
Exception
    └── ColorSchemeGeneratorError (base)
        ├── BackendNotAvailableError
        ├── ColorExtractionError
        ├── TemplateRenderError
        ├── OutputWriteError
        └── InvalidImageError
```

All exceptions inherit from `ColorSchemeGeneratorError`, making it easy to catch all module-specific errors.

---

## ColorSchemeGeneratorError

**Base exception for all colorscheme_generator errors.**

### Class Definition

```python
class ColorSchemeGeneratorError(Exception):
    """Base exception for all colorscheme_generator errors."""
```

### Usage

```python
try:
    # Any colorscheme_generator operation
    scheme = generator.generate(image_path, config)
except ColorSchemeGeneratorError as e:
    # Catches ALL module-specific errors
    print(f"Error: {e}")
```

---

## BackendNotAvailableError

**Raised when a backend is not available on the system.**

### Class Definition

```python
class BackendNotAvailableError(ColorSchemeGeneratorError):
    """Raised when backend is not available."""
    
    def __init__(self, backend: str, message: str | None = None):
        self.backend = backend
        default_message = f"Backend '{backend}' is not available"
        super().__init__(message or default_message)
```

### Attributes

- **backend:** Name of the unavailable backend

### When Raised

- Pywal backend: `pywal` library or `wal` command not found
- Wallust backend: `wallust` binary not found in PATH
- Custom backend: Never (always available)
- Factory: No backends available when using `create_auto()`

### Examples

```python
from colorscheme_generator.core.exceptions import BackendNotAvailableError
from colorscheme_generator.factory import ColorSchemeGeneratorFactory
from colorscheme_generator.config.enums import Backend

try:
    generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)
    generator.ensure_available()
except BackendNotAvailableError as e:
    print(f"Backend not available: {e.backend}")
    print(f"Error: {e}")
    # Output:
    # Backend not available: pywal
    # Error: Backend 'pywal' is not available
```

### Recovery

```python
try:
    generator = ColorSchemeGeneratorFactory.create(Backend.WALLUST, settings)
    generator.ensure_available()
except BackendNotAvailableError:
    # Fall back to custom backend
    generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
```

---

## ColorExtractionError

**Raised when color extraction from image fails.**

### Class Definition

```python
class ColorExtractionError(ColorSchemeGeneratorError):
    """Raised when color extraction fails."""
    
    def __init__(self, backend: str, image_path: Path, message: str | None = None):
        self.backend = backend
        self.image_path = image_path
        default_message = f"Failed to extract colors from {image_path} using {backend}"
        super().__init__(message or default_message)
```

### Attributes

- **backend:** Backend that failed
- **image_path:** Path to the image that failed

### When Raised

- Backend command fails (non-zero exit code)
- Backend output is invalid/unparseable
- Image processing fails (corrupt image, unsupported format)
- Algorithm fails (K-means doesn't converge, etc.)

### Examples

```python
from colorscheme_generator.core.exceptions import ColorExtractionError

try:
    scheme = generator.generate(Path("~/wallpapers/image.png"), config)
except ColorExtractionError as e:
    print(f"Backend: {e.backend}")
    print(f"Image: {e.image_path}")
    print(f"Error: {e}")
    # Output:
    # Backend: pywal
    # Image: /home/user/wallpapers/image.png
    # Error: Failed to extract colors from /home/user/wallpapers/image.png using pywal
```

### Recovery

```python
try:
    scheme = generator.generate(image_path, config)
except ColorExtractionError as e:
    # Try different backend
    fallback_generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
    scheme = fallback_generator.generate(image_path, config)
```

---

## TemplateRenderError

**Raised when Jinja2 template rendering fails.**

### Class Definition

```python
class TemplateRenderError(ColorSchemeGeneratorError):
    """Raised when template rendering fails."""
    
    def __init__(self, template: str, message: str | None = None):
        self.template = template
        default_message = f"Failed to render template '{template}'"
        super().__init__(message or default_message)
```

### Attributes

- **template:** Name of the template that failed

### When Raised

- Template file not found
- Template syntax error
- Template variable missing
- Jinja2 rendering error

### Examples

```python
from colorscheme_generator.core.exceptions import TemplateRenderError

try:
    output_files = manager.write_outputs(scheme, output_dir, formats)
except TemplateRenderError as e:
    print(f"Template: {e.template}")
    print(f"Error: {e}")
    # Output:
    # Template: colors.json.j2
    # Error: Failed to render template 'colors.json.j2'
```

### Recovery

```python
try:
    output_files = manager.write_outputs(
        scheme,
        output_dir,
        [ColorFormat.JSON, ColorFormat.CSS, ColorFormat.YAML]
    )
except TemplateRenderError as e:
    # Skip failed format, continue with others
    formats_to_retry = [f for f in formats if f.value != e.template.replace('.j2', '')]
    output_files = manager.write_outputs(scheme, output_dir, formats_to_retry)
```

---

## OutputWriteError

**Raised when writing output file fails.**

### Class Definition

```python
class OutputWriteError(ColorSchemeGeneratorError):
    """Raised when writing output file fails."""
    
    def __init__(self, path: Path, message: str | None = None):
        self.path = path
        default_message = f"Failed to write output file '{path}'"
        super().__init__(message or default_message)
```

### Attributes

- **path:** Path to the file that failed to write

### When Raised

- Permission denied
- Disk full
- Invalid path
- Directory doesn't exist (and can't be created)

### Examples

```python
from colorscheme_generator.core.exceptions import OutputWriteError

try:
    output_files = manager.write_outputs(scheme, output_dir, formats)
except OutputWriteError as e:
    print(f"Path: {e.path}")
    print(f"Error: {e}")
    # Output:
    # Path: /root/colors/colors.json
    # Error: Failed to write output file '/root/colors/colors.json'
```

### Recovery

```python
try:
    output_files = manager.write_outputs(scheme, output_dir, formats)
except OutputWriteError as e:
    # Try fallback directory
    fallback_dir = Path.home() / ".cache/colorscheme"
    output_files = manager.write_outputs(scheme, fallback_dir, formats)
```

---

## InvalidImageError

**Raised when image file is invalid or cannot be read.**

### Class Definition

```python
class InvalidImageError(ColorSchemeGeneratorError):
    """Raised when image is invalid."""
    
    def __init__(self, image_path: Path, message: str | None = None):
        self.image_path = image_path
        default_message = f"Invalid image file: {image_path}"
        super().__init__(message or default_message)
```

### Attributes

- **image_path:** Path to the invalid image

### When Raised

- Image file doesn't exist
- File is not a valid image
- Unsupported image format
- Corrupt image file
- Permission denied

### Examples

```python
from colorscheme_generator.core.exceptions import InvalidImageError

try:
    scheme = generator.generate(Path("~/wallpapers/missing.png"), config)
except InvalidImageError as e:
    print(f"Image: {e.image_path}")
    print(f"Error: {e}")
    # Output:
    # Image: /home/user/wallpapers/missing.png
    # Error: Invalid image file: /home/user/wallpapers/missing.png
```

### Recovery

```python
try:
    scheme = generator.generate(image_path, config)
except InvalidImageError as e:
    # Use default/fallback image
    fallback_image = Path("/usr/share/backgrounds/default.png")
    scheme = generator.generate(fallback_image, config)
```

---

## Error Handling Patterns

### Pattern 1: Catch All Module Errors

```python
from colorscheme_generator.core.exceptions import ColorSchemeGeneratorError

try:
    generator = ColorSchemeGeneratorFactory.create_auto(settings)
    scheme = generator.generate(image_path, config)
    output_files = manager.write_outputs(scheme, output_dir, formats)
except ColorSchemeGeneratorError as e:
    print(f"Colorscheme generation failed: {e}")
    # Handle any module error
```

### Pattern 2: Specific Error Handling

```python
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
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
    raise
except ColorExtractionError as e:
    print(f"Extraction failed with {e.backend}, trying custom backend")
    generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
    scheme = generator.generate(image_path, config)
```

### Pattern 3: Graceful Degradation

```python
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    TemplateRenderError,
    OutputWriteError,
)

# Try backends in order of preference
backends_to_try = [Backend.WALLUST, Backend.PYWAL, Backend.CUSTOM]
generator = None

for backend in backends_to_try:
    try:
        gen = ColorSchemeGeneratorFactory.create(backend, settings)
        gen.ensure_available()
        generator = gen
        break
    except BackendNotAvailableError:
        continue

if not generator:
    raise RuntimeError("No backends available")

# Generate colors
scheme = generator.generate(image_path, config)

# Try to write all formats, collect successes
output_files = {}
for fmt in formats:
    try:
        files = manager.write_outputs(scheme, output_dir, [fmt])
        output_files.update(files)
    except (TemplateRenderError, OutputWriteError) as e:
        print(f"Failed to write {fmt}: {e}")
        continue

print(f"Successfully wrote {len(output_files)} files")
```

### Pattern 4: Retry with Fallback

```python
from colorscheme_generator.core.exceptions import ColorExtractionError

def generate_with_fallback(image_path, config, settings):
    """Generate colors with automatic fallback."""
    try:
        # Try preferred backend
        generator = ColorSchemeGeneratorFactory.create_auto(settings)
        return generator.generate(image_path, config)
    except ColorExtractionError:
        # Fall back to custom backend with different algorithm
        generator = ColorSchemeGeneratorFactory.create(Backend.CUSTOM, settings)
        fallback_config = GeneratorConfig.from_settings(
            settings,
            backend_options={"algorithm": "median_cut"}
        )
        return generator.generate(image_path, fallback_config)
```

### Pattern 5: Logging and Re-raising

```python
import logging
from colorscheme_generator.core.exceptions import ColorSchemeGeneratorError

logger = logging.getLogger(__name__)

try:
    scheme = generator.generate(image_path, config)
except ColorSchemeGeneratorError as e:
    logger.error(f"Color generation failed: {e}", exc_info=True)
    # Log details but re-raise for caller to handle
    raise
```

---

## Next Steps

- **[Core API](core.md)** - Core abstractions and types
- **[Troubleshooting](../reference/troubleshooting.md)** - Common issues and solutions
- **[Examples](../reference/examples.md)** - Error handling examples


# Icon Generator

Dynamic icon generation system with variant support and SVG template caching.

## Overview

The icon generator provides a flexible system for generating icons from SVG templates with support for:

- **Dynamic Discovery**: Automatically discovers icon categories and variants from filesystem
- **Variant Support**: Icons can have multiple visual styles (solid, rounded, sharp, etc.)
- **SVG Template Caching**: Integrates with cache managers for 60-70% performance improvement
- **Colorscheme-Aware**: Uses full colorscheme data for cache keys
- **Clean API**: Simple, reusable interface for integration

## Installation

```bash
cd src/common/modules/icon-generator
uv sync
```

## Usage

### Basic Example

```python
from pathlib import Path
from icon_generator import IconRegistry, IconService, IconGenerationRequest

# Create registry to discover icons
registry = IconRegistry(base_path=Path("assets/icons"))

# Create service (without cache for simplicity)
service = IconService(registry=registry)

# Generate icons
request = IconGenerationRequest(
    category="battery-icons",
    variant="solid",
    color="#ffffff",
    colorscheme_data={"color0": "#000", "color1": "#f00", ...},  # Full colorscheme
    output_dir=Path("output/battery-icons/solid"),
)

result = service.generate_icons(request)
print(result.summary())
# Output: Generated 10 icons for category 'battery-icons' (variant: solid)
```

### With Caching

```python
from icon_generator import IconRegistry, IconService

# Assume you have an SVG cache manager
# (e.g., from dotfiles-manager)
cache_manager = ...  # Your SVGTemplateCacheManager instance

service = IconService(
    registry=registry,
    cache_manager=cache_manager,
)

# First generation - cache misses
result1 = service.generate_icons(request)
print(f"Cache hits: {result1.cache_hits}, misses: {result1.cache_misses}")
# Output: Cache hits: 0, misses: 10

# Second generation with same colorscheme - cache hits!
result2 = service.generate_icons(request)
print(f"Cache hits: {result2.cache_hits}, misses: {result2.cache_misses}")
# Output: Cache hits: 10, misses: 0
```

## Directory Structure

The icon generator supports two directory structures:

### 1. Categories with Variants

```
assets/icons/
├── battery-icons/              # Category
│   ├── solid/                  # Variant
│   │   ├── battery-0.svg
│   │   ├── battery-25.svg
│   │   └── battery-100.svg
│   ├── rounded/                # Variant
│   │   └── ...
│   └── sharp/                  # Variant
│       └── ...
└── network-icons/              # Category
    ├── solid/
    │   └── wifi-high.svg
    └── rounded/
        └── ...
```

### 2. Categories without Variants (Flat)

```
assets/icons/
└── wlogout-icons/              # Category (no variants)
    ├── lock.svg
    ├── logout.svg
    └── shutdown.svg
```

## API Reference

### IconRegistry

Discovers and manages icon categories and variants.

```python
registry = IconRegistry(base_path=Path("assets/icons"))

# Get category metadata
category = registry.get_category("battery-icons")
print(category.has_variants)  # True
print(category.list_variants())  # ['solid', 'rounded', 'sharp']

# List all categories
categories = registry.list_categories()  # ['battery-icons', 'network-icons', ...]
```

### IconService

Generates icons with template rendering and caching.

```python
service = IconService(
    registry=registry,
    cache_manager=cache_manager,  # Optional
    renderer=svg_renderer,        # Optional
)

result = service.generate_icons(request)
```

### IconGenerationRequest

Request for generating icons.

```python
request = IconGenerationRequest(
    category="battery-icons",
    variant="solid",  # Or None for categories without variants
    color="#ffffff",  # Primary color for {{CURRENT_COLOR}} placeholder
    colorscheme_data={...},  # Full colorscheme for cache hashing
    output_dir=Path("output"),
    icons=["battery-0", "battery-25"],  # Optional: specific icons, or None for all
    context={"CUSTOM_VAR": "value"},  # Optional: additional template variables
)
```

### IconGenerationResult

Result of icon generation with statistics.

```python
result = service.generate_icons(request)

print(result.generated_icons)  # {'battery-0': Path(...), 'battery-25': Path(...)}
print(result.cache_hits)  # 2
print(result.cache_misses)  # 0
print(result.cache_hit_rate)  # 100.0
print(result.summary())  # Human-readable summary
```

## Integration

### With dotfiles-manager

See the dotfiles-manager documentation for integration examples using dependency injection.

### Custom Cache Manager

Implement the `SVGCacheManager` protocol:

```python
class MyCacheManager:
    def compute_colorscheme_hash(self, colorscheme_data: dict) -> str:
        # Return SHA256 hash of colorscheme
        ...

    def get_cached_svg(self, colorscheme_hash: str, template_name: str) -> str | None:
        # Return cached SVG content or None
        ...

    def cache_svg(self, colorscheme_hash: str, template_name: str, svg_content: str) -> None:
        # Store SVG content in cache
        ...
```

## Testing

```bash
uv run pytest
uv run pytest --cov=icon_generator
```

## License

Part of the dotfiles project.

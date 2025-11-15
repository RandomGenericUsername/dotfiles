# Wallpaper Orchestrator

Complete wallpaper setup tool that orchestrates wallpaper effects generation, color scheme extraction, and wallpaper setting.

## Features

- **Wallpaper Effects Generation**: Generates all available effect variants using wallpaper-effects-orchestrator
- **Color Scheme Extraction**: Extracts color schemes from original wallpaper using colorscheme-orchestrator
- **Wallpaper Setting**: Sets wallpaper using hyprpaper-manager
- **Pipeline-Based**: Uses dotfiles-pipeline for robust serial execution
- **Dual-Use Pattern**: Works as both Python module and CLI tool
- **Configurable**: Extensive configuration via TOML files

## Installation

```bash
# Install with uv
uv sync

# Or install in editable mode
make install
```

## Usage

### As CLI Tool

```bash
# Basic usage (uses defaults from config)
wallpaper-orchestrator process -i wallpaper.png

# With custom output directories
wallpaper-orchestrator process -i wallpaper.png \
    --effects-output ~/wallpapers/effects \
    --colorscheme-output ~/.config/colors

# With specific backend and monitor
wallpaper-orchestrator process -i wallpaper.png \
    --backend pywal --monitor DP-1

# Verbose output
wallpaper-orchestrator process -i wallpaper.png -v

# Process multiple wallpapers
wallpaper-orchestrator batch wallpaper1.png wallpaper2.png wallpaper3.png

# With custom settings
wallpaper-orchestrator batch *.png --backend pywal --monitor DP-1
```

### As Python Module

```python
from pathlib import Path
from wallpaper_orchestrator import WallpaperOrchestrator

# Create orchestrator (loads config from settings.toml)
orchestrator = WallpaperOrchestrator()

# Process wallpaper
result = orchestrator.process(Path("wallpaper.png"))

# Check results
print(f"Original: {result.original_wallpaper}")
print(f"Effects: {len(result.effect_variants)} variants")
print(f"Color schemes: {len(result.colorscheme_files)} files")
print(f"Wallpaper set: {result.wallpaper_set}")

# Access generated files
for effect_name, path in result.effect_variants.items():
    print(f"  • {effect_name}: {path}")

for fmt, path in result.colorscheme_files.items():
    print(f"  • {fmt}: {path}")

# Process multiple wallpapers
results = orchestrator.process_batch([
    Path("wallpaper1.png"),
    Path("wallpaper2.png"),
])
```

### With Custom Configuration

```python
from pathlib import Path
from wallpaper_orchestrator import WallpaperOrchestrator
from wallpaper_orchestrator.config import load_settings

# Load and modify config
config = load_settings()
config.colorscheme.backend = "wallust"
config.hyprpaper.monitor = "DP-1"

# Create orchestrator with custom config
orchestrator = WallpaperOrchestrator(config=config)

# Process with overrides
result = orchestrator.process(
    wallpaper_path=Path("wallpaper.png"),
    effects_output_dir=Path("~/custom/effects"),
    colorscheme_output_dir=Path("~/.config/colors"),
    monitor="HDMI-A-1",
)
```

## Configuration

Configuration is stored in `config/settings.toml`:

```toml
[orchestrator]
effects_output_dir = "~/.cache/wallpaper/effects"
colorscheme_output_dir = "~/.cache/colorscheme"
log_level = "INFO"
verbose = false

[colorscheme]
backend = "pywal"  # pywal, wallust, or custom
formats = ["json", "css", "gtk.css", "yaml", "sh"]
color_count = 16
container_runtime = "docker"

[wallpaper_effects]
container_runtime = "docker"
image_name = "wallpaper-effects-processor"
image_tag = "latest"
processing_mode = "memory"
output_format = "png"
quality = 95

[hyprpaper]
monitor = "all"  # "all", "focused", or specific monitor name
mode = "cover"  # cover, contain, tile
autostart = true
max_preload_pool_mb = 100

[pipeline]
fail_fast = true
parallel_enabled = false
```

## Pipeline Steps

The orchestrator executes three steps in series:

1. **GenerateEffectsStep**: Generates all wallpaper effect variants
   - Uses wallpaper-effects-orchestrator
   - Generates all available effects
   - Outputs to configured effects directory

2. **GenerateColorSchemeStep**: Generates color scheme from original wallpaper
   - Uses colorscheme-orchestrator
   - Extracts colors from **original** wallpaper (not processed variants)
   - Supports multiple backends (pywal, wallust, custom)
   - Outputs in multiple formats (json, css, yaml, sh)

3. **SetWallpaperStep**: Sets wallpaper using hyprpaper
   - Uses hyprpaper-manager
   - Sets **original** wallpaper (not processed variants)
   - Supports monitor selection (all, focused, specific)
   - Configurable display mode (cover, contain, tile)

## Result Metadata

The `WallpaperResult` object contains complete metadata:

```python
@dataclass
class WallpaperResult:
    # Original wallpaper
    original_wallpaper: Path

    # Output directories
    effects_output_dir: Path
    colorscheme_output_dir: Path

    # Generated files
    effect_variants: dict[str, Path]  # effect_name → path
    colorscheme_files: dict[str, Path]  # format → path

    # Wallpaper set status
    wallpaper_set: bool
    monitor_set: str | None

    # Metadata
    timestamp: datetime
    success: bool
    errors: list[str]
```

## Development

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run tests
make test

# Run all checks
make all-checks

# Clean cache files
make clean
```

## Dependencies

- **colorscheme-orchestrator**: Color scheme generation
- **wallpaper-effects-orchestrator**: Wallpaper effects processing
- **hyprpaper-manager**: Hyprpaper wallpaper management
- **dotfiles-pipeline**: Pipeline execution framework
- **dotfiles-logging**: Logging utilities
- **typer**: CLI framework
- **rich**: Terminal output formatting
- **pydantic**: Configuration validation
- **dynaconf**: Configuration management

## Architecture

```
wallpaper-orchestrator/
├── config/
│   └── settings.toml          # Configuration
├── src/
│   └── wallpaper_orchestrator/
│       ├── __init__.py        # Package exports
│       ├── __main__.py        # python -m entry point
│       ├── cli.py             # Typer CLI
│       ├── orchestrator.py    # Main orchestrator
│       ├── types.py           # Result types
│       ├── config/            # Configuration models
│       │   ├── __init__.py
│       │   └── settings.py
│       └── steps/             # Pipeline steps
│           ├── __init__.py
│           ├── effects_step.py
│           ├── colorscheme_step.py
│           └── wallpaper_step.py
├── pyproject.toml
├── Makefile
└── README.md
```

## License

MIT

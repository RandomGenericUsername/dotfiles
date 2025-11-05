# Hyprpaper Manager

Python API and CLI for managing hyprpaper wallpapers with full IPC control.

## Features

- 🎨 **Type-Safe API**: Full Pydantic models and type hints
- 🔌 **IPC Control**: Complete hyprctl wrapper with timeout/error handling
- 🖥️ **Monitor Management**: Query and manage multiple monitors
- 🔍 **Smart Path Resolution**: Automatically resolves absolute paths, relative paths, or searches configured directories
- 🎲 **Random Wallpapers**: Built-in random selection with exclusion
- ⚙️ **Configuration**: Dynaconf-based config with sensible defaults
- 🖥️ **CLI Tool**: Rich-based CLI for interactive use
- ✅ **Error Handling**: Comprehensive exception hierarchy

## Installation

```bash
# Install with uv
uv sync

# Or install in editable mode
make install
```

## Quick Start

### Python API

```python
from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.core.types import WallpaperMode, MonitorSelector

# Initialize manager
manager = HyprpaperManager()

# Check if running
if not manager.is_running():
    print("hyprpaper is not running!")

# Smart path resolution:
# 1. Just a name → searches in configured dirs
manager.set_wallpaper("mountain.jpg")

# 2. Absolute path → uses directly
manager.set_wallpaper("/home/user/Pictures/beach.png", monitor="DP-1")

# 3. Relative path → resolves from current directory
manager.set_wallpaper("./wallpapers/forest.jpg")

# Set wallpaper for focused monitor
manager.set_wallpaper("forest.jpg", monitor=MonitorSelector.FOCUSED)

# Set with different mode
manager.set_wallpaper("pattern.png", mode=WallpaperMode.TILE)

# Set random wallpaper
wallpaper = manager.set_random_wallpaper()
print(f"Set random wallpaper: {wallpaper}")

# Get status
status = manager.get_status()
print(f"Loaded: {status.loaded_wallpapers}")
print(f"Active: {status.active_wallpapers}")

# List available wallpapers
wallpapers = manager.list_wallpapers()
for wp in wallpapers:
    print(wp)

# Get monitors
monitors = manager.get_monitors()
for mon in monitors:
    print(f"{mon.name}: {mon.current_wallpaper}")
```

### CLI

```bash
# Show status
hyprpaper-manager status

# Set wallpaper
hyprpaper-manager set mountain.jpg
hyprpaper-manager set ~/Pictures/beach.png --monitor DP-1
hyprpaper-manager set pattern.png --mode tile

# Set random wallpaper
hyprpaper-manager random
hyprpaper-manager random --monitor focused

# List wallpapers
hyprpaper-manager list

# List monitors
hyprpaper-manager monitors
```

## Configuration

Create `config/settings.toml` or `~/.config/hyprpaper-manager/settings.toml`:

```toml
[hyprpaper]
# Config file location
config_file = "~/.config/hypr/hyprpaper.conf"

# IPC settings
ipc_enabled = true

# Splash settings
splash_enabled = false
splash_offset = 2.0
splash_color = "55ffffff"

# Wallpaper directories
wallpaper_dirs = [
    "~/Pictures/wallpapers",
    "~/wallpapers",
]

# Behavior
auto_unload_unused = true
preload_on_set = false  # Use fast reload by default
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

# Install pre-commit hooks
make pre-commit-install
```

## API Reference

See [docs/api.md](docs/api.md) for detailed API documentation.

## License

MIT

# Hyprpaper Manager

Python API and CLI for managing hyprpaper wallpapers with full IPC control.

## Features

- 🎨 **Type-Safe API**: Full Pydantic models and type hints
- 🔌 **IPC Control**: Complete hyprctl wrapper with timeout/error handling
- 🖥️ **Monitor Management**: Query and manage multiple monitors
- 🔍 **Smart Path Resolution**: Automatically resolves absolute paths, relative paths, or searches configured directories
- 🧠 **Smart Pool Management**: Automatic memory management with configurable size limits
- 🛡️ **Size Protection**: Prevents loading wallpapers that exceed size limits
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

### First Time Setup

The manager will automatically create `~/.config/hypr/hyprpaper.conf` if it doesn't exist (controlled by `auto_create_config` setting, enabled by default).

Then start hyprpaper:
```bash
hyprpaper &
```

### Python API

```python
from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.core.types import WallpaperMode, MonitorSelector

# Initialize manager
manager = HyprpaperManager()

# Check if running
if not manager.is_running():
    print("hyprpaper is not running!")

# Simple usage - set() handles everything automatically
manager.set("mountain.jpg")  # Auto-preloads, sets, manages pool

# Smart path resolution:
# 1. Just a name → searches in configured dirs
manager.set("mountain.jpg")

# 2. Absolute path → uses directly
manager.set("/home/user/Pictures/beach.png", monitor="DP-1")

# 3. Relative path → resolves from current directory
manager.set("./wallpapers/forest.jpg")

# Power user - preload pool for instant switching
manager.preload_batch(["wp1.jpg", "wp2.jpg", "wp3.jpg"])
manager.set("wp1.jpg")  # Instant! Already preloaded
manager.set("wp2.jpg")  # Instant! Already preloaded

# Check pool status
status = manager.get_pool_status()
print(f"Pool: {status['total_size_mb']}MB / {status['max_size_mb']}MB")
print(f"Usage: {status['usage_percent']}%")

# Set random wallpaper
wallpaper = manager.set_random_wallpaper()
print(f"Set random wallpaper: {wallpaper}")

# Manual pool management
manager.unload_unused()  # Remove wallpapers not displayed
manager.unload_all()  # Clear entire pool

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

# Set wallpaper with custom directory
hyprpaper-manager set wallpaper.jpg -d ~/my-wallpapers -d ~/Downloads

# Set random wallpaper
hyprpaper-manager random
hyprpaper-manager random --monitor focused

# List wallpapers
hyprpaper-manager list

# List wallpapers from custom directories
hyprpaper-manager list -d ~/my-wallpapers -d ~/Downloads

# List monitors
hyprpaper-manager monitors

# Preload wallpaper
hyprpaper-manager preload wallpaper.jpg

# Unload wallpaper
hyprpaper-manager unload wallpaper.jpg
hyprpaper-manager unload unused
hyprpaper-manager unload all
```

**CLI Options:**

All wallpaper-related commands (`set`, `random`, `list`, `preload`, `unload`) support the `--wallpaper-dir` / `-d` option to override configured wallpaper directories:

```bash
# Use custom directories instead of configured ones
hyprpaper-manager set mountain.jpg -d ~/custom-wallpapers
hyprpaper-manager random -d ~/wallpapers -d ~/Downloads
hyprpaper-manager list -d ~/Pictures
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
auto_create_config = true

# Memory management
max_preload_pool_mb = 100  # Maximum memory for preloaded wallpapers pool
max_wallpaper_size_multiplier = 2.0  # Max single wallpaper = pool_size * multiplier
```

### Pool Management

The pool management system automatically handles memory:

- **`max_preload_pool_mb`**: Maximum memory (MB) for the wallpaper pool (default: 100MB)
- **`max_wallpaper_size_multiplier`**: Maximum single wallpaper size = pool_size × multiplier (default: 2.0)
  - Example: 100MB pool × 2.0 = 200MB max single wallpaper
- **`auto_unload_unused`**: Automatically unload wallpapers not displayed (default: true)

**Cleanup Strategy:**
1. Remove unused wallpapers first (not displayed on any monitor)
2. Remove oldest wallpapers (LRU order)
3. Never remove currently displayed wallpapers

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

## Changelog

### Recent Fixes

**Bug Fixes:**
- Fixed critical bug where wallpapers were never actually preloaded to hyprpaper (wallpaper was added to pool tracking before checking if it needed preloading, causing the preload check to always pass)
- Fixed IPC response parsing to properly handle "no wallpapers loaded" and "no wallpapers active" responses from hyprpaper
- Fixed black background issue on first command (caused by wallpapers not being preloaded)

**Enhancements:**
- Added `--wallpaper-dir` / `-d` CLI option to all wallpaper-related commands (`set`, `random`, `list`, `preload`, `unload`) to override configured wallpaper directories
- Improved CLI flexibility for users who don't want to rely on configuration files

## License

MIT

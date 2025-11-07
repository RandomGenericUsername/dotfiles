# Hyprpaper Manager

Python API and CLI for managing hyprpaper wallpapers with full IPC control.

## Features

- 🎨 **Type-Safe API**: Full Pydantic models and type hints
- 🔌 **IPC Control**: Complete hyprctl wrapper with timeout/error handling
- 🔄 **Auto-Retry Logic**: Automatic retry with exponential backoff for transient failures
- 🚀 **Startup Race Fix**: Handles hyprpaper startup delays automatically (no more black wallpapers!)
- ⚡ **Auto-Start**: Automatically starts hyprpaper if not running (enabled by default)
- 🖥️ **Monitor Management**: Query and manage multiple monitors
- 🔍 **Smart Path Resolution**: Automatically resolves absolute paths, relative paths, or searches configured directories
- 🧠 **Smart Pool Management**: Automatic memory management with configurable size limits
- 🛡️ **Size Protection**: Prevents loading wallpapers that exceed size limits
- 🎲 **Random Wallpapers**: Built-in random selection with exclusion
- ⚙️ **Configuration**: Dynaconf-based config with sensible defaults
- 🖥️ **CLI Tool**: Rich-based CLI for interactive use
- 📝 **Comprehensive Logging**: Debug logging with `--verbose` flag
- ✅ **Error Handling**: Comprehensive exception hierarchy with context-aware messages

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

**No need to manually start hyprpaper!** The manager will automatically start it when needed (controlled by `autostart` setting, enabled by default).

If you prefer to manage hyprpaper manually, disable autostart in `config/settings.toml`:
```toml
autostart = false
```

Then start hyprpaper manually:
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

# Enable debug logging (NEW in v0.2.0)
hyprpaper-manager set wallpaper.jpg --verbose
hyprpaper-manager status --verbose

# Or use environment variable
HYPRPAPER_MANAGER_LOG_LEVEL=DEBUG hyprpaper-manager set wallpaper.jpg
```

**CLI Options:**

All wallpaper-related commands (`set`, `random`, `list`, `preload`, `unload`) support:
- `--wallpaper-dir` / `-d`: Override configured wallpaper directories
- `--verbose` / `-v`: Enable debug logging (NEW in v0.2.0)

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
ipc_timeout = 5              # Default command timeout in seconds (NEW in v0.2.0)
ipc_retry_attempts = 3       # Number of retry attempts (NEW in v0.2.0)
ipc_retry_delay = 0.5        # Initial retry delay in seconds (NEW in v0.2.0)
ipc_startup_wait = 2.0       # Max wait for socket on startup (NEW in v0.2.0)

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
autostart = true             # Automatically start hyprpaper if not running (NEW in v0.2.1)

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

## Troubleshooting

### "hyprpaper is not running"

**With autostart enabled (default)**: This should not happen! The manager automatically starts hyprpaper.

**With autostart disabled**: Start hyprpaper in the background:
```bash
hyprpaper &
```

### "Failed to autostart hyprpaper"

**Cause**: hyprpaper command not found or failed to start.

**Solution**:
1. Check if hyprpaper is installed: `which hyprpaper`
2. Install hyprpaper if missing
3. Check hyprpaper logs for errors
4. Try starting manually: `hyprpaper &`

### "hyprpaper IPC socket not ready"

**Cause**: hyprpaper is starting up or crashed.

**Solution**:
1. Check if hyprpaper is running: `pgrep hyprpaper`
2. Check hyprpaper logs: `journalctl --user -u hyprpaper -f`
3. Restart hyprpaper: `pkill hyprpaper && hyprpaper &`

### Black wallpaper on first command

**Fixed in v0.2.0!** This was caused by a race condition during hyprpaper startup.

If you still experience this:
1. Update to v0.2.0 or later
2. Enable debug logging: `hyprpaper-manager set wallpaper.jpg --verbose`
3. Check if socket readiness check is working

### Commands taking too long

**Cause**: Retry logic and socket readiness checks (added in v0.2.0 for reliability).

**Solution**: Adjust configuration:
```toml
[hyprpaper]
ipc_retry_attempts = 1    # Reduce retries
ipc_startup_wait = 0.5    # Shorter wait
```

### Enable Debug Logging

```bash
# CLI
hyprpaper-manager set wallpaper.jpg --verbose

# Environment variable
HYPRPAPER_MANAGER_LOG_LEVEL=DEBUG hyprpaper-manager set wallpaper.jpg

# Python API
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference

See [docs/api.md](docs/api.md) for detailed API documentation.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### v0.2.0 - Major Reliability Update

**Critical Fixes:**
- 🔴 Fixed race condition on hyprpaper startup (no more black wallpapers!)
- 🔴 Fixed empty error messages when IPC commands fail
- 🟡 Added automatic retry logic with exponential backoff
- 🟡 Added comprehensive logging support
- 🟡 Made timeouts configurable per-command

**New Features:**
- `HyprpaperIPC.is_ready()` - Check if socket is ready
- Per-command timeout overrides
- `--verbose` / `-v` CLI flag for debug logging
- `HYPRPAPER_MANAGER_LOG_LEVEL` environment variable

See [MIGRATION_v0.2.md](docs/MIGRATION_v0.2.md) for migration guide.

## License

MIT

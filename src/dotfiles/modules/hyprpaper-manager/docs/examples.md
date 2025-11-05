# Usage Examples

## Basic Usage

### Setting a Wallpaper

```python
from hyprpaper_manager import HyprpaperManager

manager = HyprpaperManager()

# Just a name - searches in configured wallpaper directories
manager.set_wallpaper("mountain.jpg")
manager.set_wallpaper("mountain")  # Auto-detects extension

# Absolute path - uses directly
manager.set_wallpaper("/home/user/Pictures/beach.png")

# Relative path - resolves from current directory
manager.set_wallpaper("./wallpapers/forest.jpg")

# Set wallpaper for specific monitor
manager.set_wallpaper("beach.png", monitor="DP-1")

# Set wallpaper for focused monitor
from hyprpaper_manager.core.types import MonitorSelector
manager.set_wallpaper("forest.jpg", monitor=MonitorSelector.FOCUSED)
```

### Smart Path Resolution

The `set_wallpaper` method intelligently resolves paths:

```python
from hyprpaper_manager import HyprpaperManager

manager = HyprpaperManager()

# 1. Just a name → searches in configured dirs
#    (e.g., ~/Pictures/wallpapers, ~/wallpapers)
manager.set_wallpaper("mountain.jpg")

# 2. Absolute path → uses directly
manager.set_wallpaper("/home/user/Downloads/wallpaper.png")
manager.set_wallpaper("~/Pictures/custom/beach.jpg")  # ~ is expanded

# 3. Relative path → resolves from current directory
manager.set_wallpaper("./my-wallpapers/forest.jpg")
manager.set_wallpaper("../shared/pattern.png")
```

### Different Display Modes

```python
from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.core.types import WallpaperMode

manager = HyprpaperManager()

# Cover mode (default)
manager.set_wallpaper("wallpaper.jpg", mode=WallpaperMode.COVER)

# Contain mode
manager.set_wallpaper("wallpaper.jpg", mode=WallpaperMode.CONTAIN)

# Tile mode
manager.set_wallpaper("pattern.png", mode=WallpaperMode.TILE)
```

### Random Wallpapers

```python
from hyprpaper_manager import HyprpaperManager

manager = HyprpaperManager()

# Set random wallpaper for all monitors
wallpaper = manager.set_random_wallpaper()
print(f"Set random wallpaper: {wallpaper}")

# Set random wallpaper for specific monitor
wallpaper = manager.set_random_wallpaper(monitor="DP-1")
```

## Status and Information

### Check Status

```python
from hyprpaper_manager import HyprpaperManager

manager = HyprpaperManager()

# Check if running
if not manager.is_running():
    print("hyprpaper is not running!")
    exit(1)

# Get full status
status = manager.get_status()
print(f"Loaded wallpapers: {status.loaded_wallpapers}")
print(f"Active wallpapers: {status.active_wallpapers}")
print(f"Monitors: {status.monitors}")
```

### List Wallpapers

```python
from hyprpaper_manager import HyprpaperManager

manager = HyprpaperManager()

# List all available wallpapers
wallpapers = manager.list_wallpapers()
for wp in wallpapers:
    print(f"  • {wp.name}")
```

### Monitor Information

```python
from hyprpaper_manager import HyprpaperManager

manager = HyprpaperManager()

# Get all monitors
monitors = manager.get_monitors()
for mon in monitors:
    print(f"{mon.name}: {mon.current_wallpaper}")

# Get focused monitor
focused = manager.get_focused_monitor()
print(f"Focused: {focused.name}")
```

## Advanced Usage

### Custom Configuration

```python
from pathlib import Path
from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.config.config import HyprpaperConfig

# Create custom config
config = HyprpaperConfig(
    wallpaper_dirs=[
        Path.home() / "Pictures/wallpapers",
        Path.home() / "Downloads",
    ],
    auto_unload_unused=True,
    preload_on_set=False,  # Use fast reload
)

# Initialize with custom config
manager = HyprpaperManager(config=config)
```

### Manual Preload/Unload

```python
from hyprpaper_manager import HyprpaperManager

manager = HyprpaperManager()

# Preload wallpaper
manager.preload_wallpaper("wallpaper1.jpg")
manager.preload_wallpaper("wallpaper2.jpg")

# Set without preloading (already in memory)
manager.set_wallpaper("wallpaper1.jpg")

# Unload specific wallpaper
manager.unload_wallpaper("wallpaper2.jpg")

# Unload all unused wallpapers
manager.unload_wallpaper("unused")

# Unload all wallpapers
manager.unload_wallpaper("all")
```

### Error Handling

```python
from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.core.exceptions import (
    HyprpaperError,
    HyprpaperNotRunningError,
    WallpaperNotFoundError,
)

manager = HyprpaperManager()

try:
    manager.set_wallpaper("nonexistent.jpg")
except WallpaperNotFoundError as e:
    print(f"Wallpaper not found: {e}")
except HyprpaperNotRunningError as e:
    print(f"hyprpaper is not running: {e}")
except HyprpaperError as e:
    print(f"Error: {e}")
```

## Script Examples

### Random Wallpaper Script

```python
#!/usr/bin/env python3
"""Set random wallpaper on all monitors."""

from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.core.exceptions import HyprpaperError

def main():
    try:
        manager = HyprpaperManager()
        wallpaper = manager.set_random_wallpaper()
        print(f"✓ Set random wallpaper: {wallpaper.name}")
    except HyprpaperError as e:
        print(f"✗ Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
```

### Wallpaper Rotator

```python
#!/usr/bin/env python3
"""Rotate through wallpapers every N seconds."""

import time
from hyprpaper_manager import HyprpaperManager

def main():
    manager = HyprpaperManager()
    interval = 300  # 5 minutes

    print(f"Rotating wallpapers every {interval} seconds...")

    while True:
        try:
            wallpaper = manager.set_random_wallpaper()
            print(f"Set: {wallpaper.name}")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
```

### Per-Monitor Wallpapers

```python
#!/usr/bin/env python3
"""Set different wallpapers for each monitor."""

from hyprpaper_manager import HyprpaperManager

def main():
    manager = HyprpaperManager()

    # Get all monitors
    monitors = manager.get_monitors()

    # Get all wallpapers
    wallpapers = manager.list_wallpapers()

    if len(wallpapers) < len(monitors):
        print("Not enough wallpapers for all monitors!")
        return

    # Set different wallpaper for each monitor
    for i, monitor in enumerate(monitors):
        wallpaper = wallpapers[i]
        manager.set_wallpaper(wallpaper, monitor=monitor.name)
        print(f"Set {monitor.name}: {wallpaper.name}")

if __name__ == "__main__":
    main()
```

## CLI Examples

```bash
# Show status
hyprpaper-manager status

# Set wallpaper
hyprpaper-manager set mountain.jpg
hyprpaper-manager set ~/Pictures/beach.png --monitor DP-1
hyprpaper-manager set pattern.png --mode tile

# Random wallpaper
hyprpaper-manager random
hyprpaper-manager random --monitor focused

# List wallpapers
hyprpaper-manager list

# List monitors
hyprpaper-manager monitors

# Preload wallpaper
hyprpaper-manager preload wallpaper.jpg

# Unload wallpaper
hyprpaper-manager unload wallpaper.jpg
hyprpaper-manager unload unused
hyprpaper-manager unload all
```

## Integration with Hyprland

### Keybinding for Random Wallpaper

Add to `~/.config/hypr/hyprland.conf`:

```ini
# Random wallpaper
bind = SUPER, W, exec, hyprpaper-manager random

# Random wallpaper on focused monitor
bind = SUPER SHIFT, W, exec, hyprpaper-manager random --monitor focused
```

### Auto-start Script

Add to `~/.config/hypr/hyprland.conf`:

```ini
# Start hyprpaper
exec-once = hyprpaper &

# Set initial wallpaper
exec-once = sleep 1 && hyprpaper-manager random
```

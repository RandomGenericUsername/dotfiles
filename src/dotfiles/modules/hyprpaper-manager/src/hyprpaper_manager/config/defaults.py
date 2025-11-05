"""Default configuration values."""

from pathlib import Path
from typing import Any

# Default hyprpaper configuration
HYPRPAPER_DEFAULTS: dict[str, Any] = {
    "config_file": Path.home() / ".config/hypr/hyprpaper.conf",
    "ipc_enabled": True,
    "splash_enabled": False,
    "splash_offset": 2.0,
    "splash_color": "55ffffff",
    "wallpaper_dirs": [
        Path.home() / "Pictures/wallpapers",
        Path.home() / "wallpapers",
    ],
    "auto_unload_unused": True,
    "preload_on_set": False,
}

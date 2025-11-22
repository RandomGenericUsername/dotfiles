"""Client for querying dotfiles-manager state."""

import json
from pathlib import Path
from typing import Any

from dotfiles_state_manager import SQLiteBackend, StateManager


class ManagerClient:
    """Client for querying dotfiles-manager state."""

    def __init__(self, manager_path: Path):
        """Initialize client.

        Args:
            manager_path: Path to dotfiles-manager module
        """
        self.manager_path = manager_path
        self.state_file = manager_path / "state" / "system.db"
        # Create StateManager with SQLite backend
        backend = SQLiteBackend(db_path=self.state_file)
        self._state_manager = StateManager(backend=backend)

    def get_system_attributes(self) -> dict[str, Any]:
        """Get system attributes from manager state.

        Returns:
            Dict with font_family, font_size, monitors

        Raises:
            RuntimeError: If state cannot be read
        """
        try:
            font_family = (
                self._state_manager.get("system:font_family")
                or "JetBrains Mono"
            )
            font_size_str = self._state_manager.get("system:font_size") or "14"
            font_size = int(font_size_str)

            # Get monitors list
            monitors_count_str = (
                self._state_manager.get("system:monitors:count") or "0"
            )
            monitors_count = int(monitors_count_str)
            monitors = []
            for i in range(monitors_count):
                monitor = self._state_manager.get(f"system:monitors:{i}")
                if monitor:
                    monitors.append(monitor)

            return {
                "font_family": font_family,
                "font_size": font_size,
                "monitors": monitors,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to read system attributes: {e}") from e

    def get_current_colorscheme(self) -> dict[str, Any]:
        """Get current colorscheme from cache.

        Returns:
            Colorscheme dict with special, colors, metadata

        Raises:
            FileNotFoundError: If colorscheme file doesn't exist
            RuntimeError: If colorscheme cannot be parsed
        """
        colorscheme_file = Path.home() / ".cache/colorscheme/colors.json"

        if not colorscheme_file.exists():
            raise FileNotFoundError(
                f"Colorscheme file not found: {colorscheme_file}. "
                "Run 'dotfiles-manager change-wallpaper' first."
            )

        try:
            with open(colorscheme_file) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse colorscheme JSON: {e}") from e

    def get_current_wallpaper(self, monitor: str = "default") -> Path | None:
        """Get current wallpaper for a monitor.

        Args:
            monitor: Monitor name (default: "default")

        Returns:
            Path to current wallpaper or None if not set
        """
        wallpaper_path_str = self._state_manager.get(
            f"system:wallpapers:{monitor}"
        )
        if not wallpaper_path_str:
            return None
        return Path(wallpaper_path_str)

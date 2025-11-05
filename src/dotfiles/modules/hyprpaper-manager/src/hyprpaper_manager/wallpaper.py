"""Wallpaper operations and discovery."""

import random
from collections.abc import Iterator
from pathlib import Path

from hyprpaper_manager.config.config import HyprpaperConfig
from hyprpaper_manager.core.exceptions import WallpaperNotFoundError


class WallpaperFinder:
    """Find wallpapers in configured directories."""

    SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

    def __init__(self, config: HyprpaperConfig):
        """Initialize wallpaper finder.

        Args:
            config: Hyprpaper configuration
        """
        self.config = config

    def find_wallpapers(self) -> list[Path]:
        """Find all wallpapers in configured directories.

        Returns:
            List of wallpaper paths
        """
        wallpapers: list[Path] = []
        for directory in self.config.wallpaper_dirs:
            if directory.exists() and directory.is_dir():
                wallpapers.extend(self._scan_directory(directory))
        return sorted(wallpapers)

    def _scan_directory(self, directory: Path) -> Iterator[Path]:
        """Scan directory for wallpapers.

        Args:
            directory: Directory to scan

        Yields:
            Wallpaper paths
        """
        for file in directory.iterdir():
            if (
                file.is_file()
                and file.suffix.lower() in self.SUPPORTED_EXTENSIONS
            ):
                yield file

    def find_wallpaper(self, name: str) -> Path:
        """Find wallpaper by name or path.

        Smart resolution:
        1. Absolute path → use directly
        2. Relative path (contains / or ./) → resolve from current dir
        3. Just a name → search in configured wallpaper dirs

        Args:
            name: Wallpaper name or path

        Returns:
            Resolved wallpaper path

        Raises:
            WallpaperNotFoundError: If wallpaper not found
        """
        path = Path(name).expanduser()

        # Case 1: Absolute path - use directly
        if path.is_absolute():
            if path.exists():
                return path.resolve()
            raise WallpaperNotFoundError(f"Wallpaper not found: {path}")

        # Case 2: Relative path (contains / or ./) - resolve from CWD
        if "/" in name or name.startswith("./") or name.startswith("../"):
            if path.exists():
                return path.resolve()
            raise WallpaperNotFoundError(f"Wallpaper not found: {path}")

        # Case 3: Just a name - search in configured directories
        for directory in self.config.wallpaper_dirs:
            if not directory.exists():
                continue

            # Try with name as-is
            candidate = directory / name
            if candidate.exists():
                return candidate.resolve()

            # Try adding extensions if no extension provided
            if not Path(name).suffix:
                for ext in self.SUPPORTED_EXTENSIONS:
                    candidate = directory / f"{name}{ext}"
                    if candidate.exists():
                        return candidate.resolve()

        raise WallpaperNotFoundError(
            f"Wallpaper '{name}' not found in configured directories"
        )

    def get_random_wallpaper(self, exclude: Path | None = None) -> Path:
        """Get random wallpaper, optionally excluding one.

        Args:
            exclude: Wallpaper to exclude from selection

        Returns:
            Random wallpaper path

        Raises:
            WallpaperNotFoundError: If no wallpapers found
        """
        wallpapers = self.find_wallpapers()
        if exclude:
            wallpapers = [w for w in wallpapers if w != exclude]

        if not wallpapers:
            raise WallpaperNotFoundError("No wallpapers found")

        return random.choice(wallpapers)

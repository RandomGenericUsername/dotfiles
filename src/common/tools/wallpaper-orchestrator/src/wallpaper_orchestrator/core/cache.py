"""Cache manager for wallpaper processing."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

from dotfiles_state_manager import StateManager


class WallpaperCacheManager:
    """Manages caching of wallpaper effects and colorschemes.

    Uses state-manager to track cache metadata and filesystem to validate
    cached files still exist.

    Cache Strategy:
    - Effects: Stored in per-wallpaper subdirectories (already done by
      effects-orchestrator)
    - Colorschemes: Copied to cache directory, then restored to active
      location when needed
    - Metadata: Tracked in SQLite via state-manager

    Cache Key: SHA256 hash of wallpaper file content (detects changes,
    survives moves)
    """

    def __init__(
        self,
        state_manager: StateManager,
        effects_base_dir: Path,
        colorscheme_cache_dir: Path,
        colorscheme_active_dir: Path,
    ):
        """Initialize cache manager.

        Args:
            state_manager: State manager instance for metadata storage
            effects_base_dir: Base directory for effects
                (e.g., ~/.cache/wallpaper/effects)
            colorscheme_cache_dir: Cache directory for colorschemes
                (e.g., ~/.cache/wallpaper/colorschemes)
            colorscheme_active_dir: Active colorscheme directory
                (e.g., ~/.cache/colorscheme)
        """
        self.state = state_manager
        self.effects_base_dir = effects_base_dir
        self.colorscheme_cache_dir = colorscheme_cache_dir
        self.colorscheme_active_dir = colorscheme_active_dir

    def __deepcopy__(self, memo):
        """Return self for deep copy (cache manager should not be copied)."""
        return self

    def _get_cache_key(self, wallpaper_path: Path) -> str:
        """Generate cache key from wallpaper file hash.

        Uses SHA256 hash of file content for robustness:
        - Detects content changes
        - Survives file moves/renames
        - Prevents duplicate processing of same image
        """
        hash_obj = hashlib.sha256(wallpaper_path.read_bytes())
        return f"wallpaper:{hash_obj.hexdigest()}"

    def _get_wallpaper_subdir(self, wallpaper_path: Path) -> str:
        """Get subdirectory name for wallpaper (uses stem)."""
        return wallpaper_path.stem

    # === EFFECTS CACHING ===

    def is_effects_cached(
        self,
        wallpaper_path: Path,
        expected_effects: list[str],
    ) -> bool:
        """Check if effects are cached and files exist.

        Args:
            wallpaper_path: Path to wallpaper file
            expected_effects: List of effect names that should exist

        Returns:
            True if all expected effects are cached and files exist
        """
        key = self._get_cache_key(wallpaper_path)

        # Check metadata
        if not self.state.hget(key, "effects_cached"):
            return False

        # Validate files still exist
        effects_dir = self.effects_base_dir / self._get_wallpaper_subdir(
            wallpaper_path
        )

        for effect in expected_effects:
            effect_file = effects_dir / f"{effect}.png"
            if not effect_file.exists():
                return False

        return True

    def get_cached_effects(
        self,
        wallpaper_path: Path,
        expected_effects: list[str],
    ) -> dict[str, Path]:
        """Get cached effect file paths.

        Args:
            wallpaper_path: Path to wallpaper file
            expected_effects: List of effect names to retrieve

        Returns:
            Dict mapping effect names to file paths
        """
        effects_dir = self.effects_base_dir / self._get_wallpaper_subdir(
            wallpaper_path
        )

        return {
            effect: effects_dir / f"{effect}.png"
            for effect in expected_effects
        }

    def mark_effects_cached(
        self,
        wallpaper_path: Path,
        effects_dir: Path,
        effect_variants: dict[str, Path],
    ) -> None:
        """Mark effects as cached in metadata.

        Args:
            wallpaper_path: Path to wallpaper file
            effects_dir: Directory where effects were generated
            effect_variants: Dict of effect names to paths
        """
        key = self._get_cache_key(wallpaper_path)

        self.state.hset(key, "wallpaper_path", str(wallpaper_path))
        self.state.hset(key, "wallpaper_stem", wallpaper_path.stem)
        self.state.hset(key, "effects_dir", str(effects_dir))
        self.state.hset(key, "effects_cached", "true")
        self.state.hset(key, "effects_count", str(len(effect_variants)))
        self.state.hset(key, "effects_cached_at", datetime.now().isoformat())

    # === COLORSCHEME CACHING ===

    def is_colorscheme_cached(
        self,
        wallpaper_path: Path,
        expected_formats: list[str],
    ) -> bool:
        """Check if colorscheme is cached and files exist.

        Args:
            wallpaper_path: Path to wallpaper file
            expected_formats: List of formats that should exist
                (json, css, etc.)

        Returns:
            True if all expected formats are cached and files exist
        """
        key = self._get_cache_key(wallpaper_path)

        # Check metadata
        if not self.state.hget(key, "colorscheme_cached"):
            return False

        # Validate files still exist in cache
        cache_dir = self.colorscheme_cache_dir / self._get_wallpaper_subdir(
            wallpaper_path
        )

        for fmt in expected_formats:
            cache_file = cache_dir / f"colors.{fmt}"
            if not cache_file.exists():
                return False

        return True

    def get_cached_colorscheme(
        self,
        wallpaper_path: Path,
        expected_formats: list[str],
    ) -> dict[str, Path]:
        """Get cached colorscheme file paths from cache directory.

        Args:
            wallpaper_path: Path to wallpaper file
            expected_formats: List of formats to retrieve

        Returns:
            Dict mapping formats to cached file paths
        """
        cache_dir = self.colorscheme_cache_dir / self._get_wallpaper_subdir(
            wallpaper_path
        )

        return {fmt: cache_dir / f"colors.{fmt}" for fmt in expected_formats}

    def activate_colorscheme(
        self,
        wallpaper_path: Path,  # noqa: ARG002
        colorscheme_files: dict[str, Path],
    ) -> dict[str, Path]:
        """Activate colorscheme by copying to active location.

        Copies colorscheme files from cache directory to active directory
        so applications can use them.

        Note: Removes existing files first to avoid permission issues
        when overwriting root-owned files from previous container runs.

        Args:
            wallpaper_path: Path to wallpaper file (unused, for consistency)
            colorscheme_files: Dict of formats to cache file paths

        Returns:
            Dict mapping formats to active file paths
        """
        self.colorscheme_active_dir.mkdir(parents=True, exist_ok=True)

        active_files = {}

        for fmt, cache_file in colorscheme_files.items():
            active_file = self.colorscheme_active_dir / f"colors.{fmt}"

            if cache_file.exists():
                # Remove existing file first (may be owned by root)
                if active_file.exists():
                    try:
                        active_file.unlink()
                    except PermissionError:
                        # File owned by root, skip activation for this file
                        continue

                shutil.copy2(cache_file, active_file)
                active_files[fmt] = active_file

        return active_files

    def restore_colorscheme_to_active(
        self,
        wallpaper_path: Path,
        expected_formats: list[str],
    ) -> dict[str, Path]:
        """Restore cached colorscheme to active location.

        Copies files from cache directory to active colorscheme directory
        so applications can use them.

        Args:
            wallpaper_path: Path to wallpaper file
            expected_formats: List of formats to restore

        Returns:
            Dict mapping formats to active file paths
        """
        cache_dir = self.colorscheme_cache_dir / self._get_wallpaper_subdir(
            wallpaper_path
        )

        # Build dict of cache files
        cache_files = {
            fmt: cache_dir / f"colors.{fmt}" for fmt in expected_formats
        }

        # Use activate_colorscheme to copy to active directory
        return self.activate_colorscheme(wallpaper_path, cache_files)

    def mark_colorscheme_cached(
        self,
        wallpaper_path: Path,
        colorscheme_files: dict[str, Path],
    ) -> None:
        """Mark colorscheme as cached.

        Note: Files are already in the cache directory (generated directly
        there), so we just update metadata.

        Args:
            wallpaper_path: Path to wallpaper file
            colorscheme_files: Dict of formats to cache file paths
        """
        key = self._get_cache_key(wallpaper_path)

        # Get cache directory for this wallpaper
        cache_dir = self.colorscheme_cache_dir / self._get_wallpaper_subdir(
            wallpaper_path
        )

        # Update metadata
        self.state.hset(key, "wallpaper_path", str(wallpaper_path))
        self.state.hset(key, "wallpaper_stem", wallpaper_path.stem)
        self.state.hset(key, "colorscheme_cache_dir", str(cache_dir))
        self.state.hset(key, "colorscheme_cached", "true")
        self.state.hset(
            key, "colorscheme_formats", ",".join(colorscheme_files.keys())
        )
        self.state.hset(
            key, "colorscheme_cached_at", datetime.now().isoformat()
        )

    # === CACHE MANAGEMENT ===

    def is_fully_cached(
        self,
        wallpaper_path: Path,
        expected_effects: list[str],
        expected_formats: list[str],
    ) -> bool:
        """Check if both effects and colorscheme are cached.

        Args:
            wallpaper_path: Path to wallpaper file
            expected_effects: List of effect names
            expected_formats: List of colorscheme formats

        Returns:
            True if both effects and colorscheme are fully cached
        """
        return self.is_effects_cached(
            wallpaper_path, expected_effects
        ) and self.is_colorscheme_cached(wallpaper_path, expected_formats)

    def invalidate_cache(self, wallpaper_path: Path) -> None:
        """Invalidate cache for a wallpaper.

        Args:
            wallpaper_path: Path to wallpaper file
        """
        key = self._get_cache_key(wallpaper_path)
        self.state.delete(key)

    def get_cache_info(self, wallpaper_path: Path) -> dict:
        """Get cache metadata for a wallpaper.

        Args:
            wallpaper_path: Path to wallpaper file

        Returns:
            Dict of cache metadata
        """
        key = self._get_cache_key(wallpaper_path)
        return self.state.hgetall(key)

    def get_all_cached_wallpapers(self) -> list[dict]:
        """Get list of all cached wallpapers with metadata.

        Returns:
            List of dicts with wallpaper info:
            [
                {
                    "path": Path("/path/to/wallpaper.png"),
                    "stem": "wallpaper",
                    "effects_cached": True,
                    "colorscheme_cached": True,
                    "effects_cached_at": "2024-01-15T10:30:00",
                    "colorscheme_cached_at": "2024-01-15T10:30:05",
                },
                ...
            ]
        """
        all_keys = self.state.keys("wallpaper:*")
        wallpapers = []

        for key in all_keys:
            metadata = self.state.hgetall(key)
            if not metadata:
                continue

            wallpaper_path_str = metadata.get("wallpaper_path", "")
            if not wallpaper_path_str:
                continue

            wallpaper_info = {
                "path": Path(wallpaper_path_str),
                "stem": metadata.get("wallpaper_stem", ""),
                "effects_cached": metadata.get("effects_cached") == "true",
                "colorscheme_cached": (
                    metadata.get("colorscheme_cached") == "true"
                ),
                "effects_cached_at": metadata.get("effects_cached_at"),
                "colorscheme_cached_at": metadata.get("colorscheme_cached_at"),
            }

            wallpapers.append(wallpaper_info)

        return wallpapers

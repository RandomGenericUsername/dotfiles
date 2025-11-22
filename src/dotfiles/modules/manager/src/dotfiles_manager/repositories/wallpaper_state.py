"""Wallpaper state repository."""

from datetime import datetime
from pathlib import Path
from typing import Any

from dotfiles_state_manager import StateManager
from wallpaper_orchestrator import AppConfig as OrchestratorConfig

# from wallpaper_orchestrator.cache.manager import WallpaperCacheManager
from dotfiles_manager.models.wallpaper_state import WallpaperState


class WallpaperStateRepository:
    """Repository for wallpaper state (current wallpaper per monitor)."""

    def __init__(
        self,
        system_state: StateManager,
        orchestrator_cache: Any | None,  # WallpaperCacheManager,
        orchestrator_config: OrchestratorConfig,
    ):
        """Initialize repository.

        Args:
            system_state: System state manager
            orchestrator_cache: Wallpaper orchestrator cache manager (deprecated, not used)
            orchestrator_config: Wallpaper orchestrator configuration
        """
        self._system_state = system_state
        self._orchestrator_cache = orchestrator_cache
        self._orchestrator_config = orchestrator_config

    def get_current_wallpaper(self, monitor: str) -> WallpaperState | None:
        """Get current wallpaper for a monitor.

        Args:
            monitor: Monitor name

        Returns:
            WallpaperState or None if no wallpaper set
        """
        wallpaper_path_str = self._system_state.get(
            f"system:wallpapers:{monitor}"
        )
        if not wallpaper_path_str:
            return None

        # Get original wallpaper path (fallback to current path for backward compatibility)
        original_wallpaper_path_str = self._system_state.get(
            f"system:wallpapers:original:{monitor}"
        )
        if not original_wallpaper_path_str:
            original_wallpaper_path_str = wallpaper_path_str

        # Get current effect (default to "off")
        current_effect = (
            self._system_state.get(f"system:wallpapers:effect:{monitor}")
            or "off"
        )

        last_changed_str = self._system_state.get(
            f"system:wallpapers:last_changed:{monitor}"
        )
        last_changed = (
            datetime.fromisoformat(last_changed_str)
            if last_changed_str
            else datetime.now()
        )

        from_cache_str = self._system_state.get(
            f"system:wallpapers:from_cache:{monitor}"
        )
        from_cache = from_cache_str == "true"

        return WallpaperState(
            monitor=monitor,
            wallpaper_path=Path(wallpaper_path_str),
            original_wallpaper_path=Path(original_wallpaper_path_str),
            current_effect=current_effect,
            last_changed=last_changed,
            from_cache=from_cache,
        )

    def set_current_wallpaper(
        self,
        wallpaper_path: Path,
        monitor: str,
        from_cache: bool = False,
        original_wallpaper_path: Path | None = None,
        current_effect: str = "off",
    ) -> None:
        """Set current wallpaper for a monitor.

        Args:
            wallpaper_path: Path to wallpaper (could be original or effect variant)
            monitor: Monitor name
            from_cache: Whether wallpaper was loaded from cache
            original_wallpaper_path: Path to original wallpaper (defaults to wallpaper_path)
            current_effect: Name of current effect applied (default: "off")
        """
        self._system_state.set(
            f"system:wallpapers:{monitor}", str(wallpaper_path)
        )
        self._system_state.set(
            f"system:wallpapers:original:{monitor}",
            str(original_wallpaper_path or wallpaper_path),
        )
        self._system_state.set(
            f"system:wallpapers:effect:{monitor}", current_effect
        )
        self._system_state.set(
            f"system:wallpapers:last_changed:{monitor}",
            datetime.now().isoformat(),
        )
        self._system_state.set(
            f"system:wallpapers:from_cache:{monitor}",
            "true" if from_cache else "false",
        )

    def is_wallpaper_cached(self, wallpaper_path: Path) -> bool:
        """Check if wallpaper is fully cached.

        Args:
            wallpaper_path: Path to wallpaper

        Returns:
            True if wallpaper is fully cached
        """
        # Cache manager is deprecated - always return False
        return False

    def get_cache_info(self, wallpaper_path: Path) -> dict:
        """Get cache information for a wallpaper.

        Args:
            wallpaper_path: Path to wallpaper

        Returns:
            Dict with cache information
        """
        # Cache manager is deprecated - return empty dict
        return {}

    def get_all_cached_wallpapers(self) -> list[dict]:
        """Get list of all cached wallpapers.

        Returns:
            List of dicts with wallpaper info
        """
        # Cache manager is deprecated - return empty list
        return []

    def invalidate_cache(self, wallpaper_path: Path) -> None:
        """Invalidate cache for a wallpaper.

        Args:
            wallpaper_path: Path to wallpaper
        """
        # Cache manager is deprecated - do nothing
        pass

    def _get_expected_effects(self) -> list[str]:
        """Get expected effects from orchestrator config.

        Returns:
            List of effect names
        """
        # Get all available effects from the wallpaper processor factory
        from wallpaper_processor.factory import EffectFactory

        return EffectFactory.get_all_effect_names()

    def _get_expected_formats(self) -> list[str]:
        """Get expected formats from orchestrator config.

        Returns:
            List of format names
        """
        # Access orchestrator's colorscheme config
        colorscheme_config = self._orchestrator_config.colorscheme
        # formats is already a list of strings
        return colorscheme_config.formats

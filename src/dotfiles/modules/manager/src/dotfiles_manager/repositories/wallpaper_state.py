"""Wallpaper state repository."""

from datetime import datetime
from pathlib import Path

from dotfiles_state_manager import StateManager
from wallpaper_orchestrator import AppConfig as OrchestratorConfig
from wallpaper_orchestrator.cache.manager import WallpaperCacheManager

from dotfiles_manager.models.wallpaper_state import WallpaperState


class WallpaperStateRepository:
    """Repository for wallpaper state (current wallpaper per monitor)."""

    def __init__(
        self,
        system_state: StateManager,
        orchestrator_cache: WallpaperCacheManager,
        orchestrator_config: OrchestratorConfig,
    ):
        """Initialize repository.

        Args:
            system_state: System state manager
            orchestrator_cache: Wallpaper orchestrator cache manager
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
            last_changed=last_changed,
            from_cache=from_cache,
        )

    def set_current_wallpaper(
        self, wallpaper_path: Path, monitor: str, from_cache: bool = False
    ) -> None:
        """Set current wallpaper for a monitor.

        Args:
            wallpaper_path: Path to wallpaper
            monitor: Monitor name
            from_cache: Whether wallpaper was loaded from cache
        """
        self._system_state.set(
            f"system:wallpapers:{monitor}", str(wallpaper_path)
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
        # Get expected effects/formats from orchestrator config
        expected_effects = self._get_expected_effects()
        expected_formats = self._get_expected_formats()

        return self._orchestrator_cache.is_fully_cached(
            wallpaper_path,
            expected_effects,
            expected_formats,
        )

    def get_cache_info(self, wallpaper_path: Path) -> dict:
        """Get cache information for a wallpaper.

        Args:
            wallpaper_path: Path to wallpaper

        Returns:
            Dict with cache information
        """
        return self._orchestrator_cache.get_cache_info(wallpaper_path)

    def get_all_cached_wallpapers(self) -> list[dict]:
        """Get list of all cached wallpapers.

        Returns:
            List of dicts with wallpaper info
        """
        return self._orchestrator_cache.get_all_cached_wallpapers()

    def invalidate_cache(self, wallpaper_path: Path) -> None:
        """Invalidate cache for a wallpaper.

        Args:
            wallpaper_path: Path to wallpaper
        """
        self._orchestrator_cache.invalidate_cache(wallpaper_path)

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

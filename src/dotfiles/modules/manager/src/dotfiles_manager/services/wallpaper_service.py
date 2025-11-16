"""Wallpaper service for managing wallpaper changes."""

from pathlib import Path

from wallpaper_orchestrator import WallpaperOrchestrator

from dotfiles_manager.hooks.registry import HookRegistry
from dotfiles_manager.models.hook import HookContext
from dotfiles_manager.models.wallpaper_state import WallpaperState
from dotfiles_manager.repositories.system_attributes import (
    SystemAttributesRepository,
)
from dotfiles_manager.repositories.wallpaper_state import (
    WallpaperStateRepository,
)


class WallpaperService:
    """Service for managing wallpaper changes and hooks."""

    def __init__(
        self,
        orchestrator: WallpaperOrchestrator,
        wallpaper_state_repo: WallpaperStateRepository,
        system_attributes_repo: SystemAttributesRepository,
        hook_registry: HookRegistry,
    ):
        """Initialize wallpaper service.

        Args:
            orchestrator: Wallpaper orchestrator instance
            wallpaper_state_repo: Wallpaper state repository
            system_attributes_repo: System attributes repository
            hook_registry: Hook registry
        """
        self._orchestrator = orchestrator
        self._wallpaper_state_repo = wallpaper_state_repo
        self._system_attributes_repo = system_attributes_repo
        self._hook_registry = hook_registry

    def change_wallpaper(
        self,
        wallpaper_path: Path,
        monitor: str,
        force_rebuild: bool = False,
        generate_colorscheme: bool = True,
        generate_effects: bool = True,
    ) -> dict:
        """Change wallpaper and execute hooks.

        Args:
            wallpaper_path: Path to wallpaper
            monitor: Monitor name
            force_rebuild: Force rebuild containers
            generate_colorscheme: Whether to generate colorscheme (default: True)
            generate_effects: Whether to generate effects (default: True)

        Returns:
            Dict with results
        """
        # Check if cached
        from_cache = self._wallpaper_state_repo.is_wallpaper_cached(
            wallpaper_path
        )

        # Process wallpaper (generates effects and colorscheme)
        result = self._orchestrator.process(
            wallpaper_path=wallpaper_path,
            monitor=monitor,
            force_rebuild=force_rebuild,
            generate_colorscheme=generate_colorscheme,
            generate_effects=generate_effects,
        )

        # Update system state
        self._wallpaper_state_repo.set_current_wallpaper(
            wallpaper_path=wallpaper_path,
            monitor=monitor,
            from_cache=from_cache,
        )

        # Get system attributes for hooks
        system_attrs = self._system_attributes_repo.get_attributes()

        # Execute hooks
        hook_context = HookContext(
            wallpaper_path=wallpaper_path,
            colorscheme_files=result.colorscheme_files,
            font_family=system_attrs.font_family,
            font_size=system_attrs.font_size,
            monitor=monitor,
            from_cache=from_cache,
            colorscheme_generated=result.colorscheme_generated,
            effects_generated=result.effects_generated,
            config={},
        )

        hook_results = self._hook_registry.execute_all(hook_context)

        return {
            "wallpaper_path": wallpaper_path,
            "monitor": monitor,
            "from_cache": from_cache,
            "orchestrator_result": result,
            "hook_results": hook_results,
        }

    def get_current_wallpaper(self, monitor: str) -> WallpaperState | None:
        """Get current wallpaper for a monitor.

        Args:
            monitor: Monitor name

        Returns:
            WallpaperState or None
        """
        return self._wallpaper_state_repo.get_current_wallpaper(monitor)

    def is_cached(self, wallpaper_path: Path) -> bool:
        """Check if wallpaper is cached.

        Args:
            wallpaper_path: Path to wallpaper

        Returns:
            True if cached
        """
        return self._wallpaper_state_repo.is_wallpaper_cached(wallpaper_path)

    def get_all_cached_wallpapers(self) -> list[dict]:
        """Get all cached wallpapers.

        Returns:
            List of cached wallpaper info
        """
        return self._wallpaper_state_repo.get_all_cached_wallpapers()

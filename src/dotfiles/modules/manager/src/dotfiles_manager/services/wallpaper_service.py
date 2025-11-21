"""Wallpaper service for managing wallpaper changes."""

import asyncio
from pathlib import Path
from uuid import uuid4

from dotfiles_daemon import DaemonPublisher
from dotfiles_event_protocol import MessageBuilder
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
        self._publisher = DaemonPublisher()
        self._operation_id: str | None = None

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
        import time

        # Generate operation ID and track start time
        operation_id = str(uuid4())
        start_time = time.time()

        # Connect to daemon (non-blocking)
        try:
            asyncio.run(self._connect_publisher())
        except Exception:
            # Silently ignore connection errors (graceful degradation)
            pass

        # Publish operation started event
        start_message = MessageBuilder.operation_started(
            event_type="wallpaper",
            operation_id=operation_id,
            operation_name="change_wallpaper",
            parameters={
                "wallpaper_path": str(wallpaper_path),
                "monitor": monitor,
            },
        )
        self._publish_event_sync(start_message)

        try:
            # Check if cached
            from_cache = self._wallpaper_state_repo.is_wallpaper_cached(
                wallpaper_path
            )

            # Create progress callback
            progress_callback = self._create_progress_callback(operation_id)

            # Process wallpaper (generates effects and colorscheme)
            result = self._orchestrator.process(
                wallpaper_path=wallpaper_path,
                monitor=monitor,
                force_rebuild=force_rebuild,
                generate_colorscheme=generate_colorscheme,
                generate_effects=generate_effects,
                progress_callback=progress_callback,
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

            # Publish operation completed event
            duration = time.time() - start_time
            complete_message = MessageBuilder.operation_completed(
                event_type="wallpaper",
                operation_id=operation_id,
                duration_seconds=duration,
                result={"success": result.success},
            )
            self._publish_event_sync(complete_message)

            return {
                "wallpaper_path": wallpaper_path,
                "monitor": monitor,
                "from_cache": from_cache,
                "orchestrator_result": result,
                "hook_results": hook_results,
            }

        except Exception as e:
            # Publish operation failed event
            failed_message = MessageBuilder.operation_failed(
                event_type="wallpaper",
                operation_id=operation_id,
                error_code="WALLPAPER_CHANGE_FAILED",
                error_message=str(e),
            )
            self._publish_event_sync(failed_message)
            raise

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

    async def _connect_publisher(self) -> None:
        """Connect to daemon publisher (non-blocking)."""
        await self._publisher.connect(timeout=0.1)

    def _publish_event_sync(self, message: dict) -> None:
        """Publish event synchronously (fire-and-forget).

        Args:
            message: Message to publish
        """
        try:
            asyncio.run(self._publisher.publish(message))
        except Exception:
            # Silently ignore publishing errors (graceful degradation)
            pass

    def _create_progress_callback(self, operation_id: str) -> callable:
        """Create progress callback for pipeline.

        Args:
            operation_id: Unique operation identifier

        Returns:
            Progress callback function
        """

        def progress_callback(
            step_index: int, total_steps: int, step_name: str, progress: float
        ) -> None:
            """Pipeline progress callback.

            Args:
                step_index: Current step index
                total_steps: Total number of steps
                step_name: Name of current step
                progress: Overall progress percentage
            """
            # Create progress message
            message = MessageBuilder.operation_progress(
                event_type="wallpaper",
                operation_id=operation_id,
                step_id=step_name,
                step_progress=(step_index + 1) / total_steps * 100,
                overall_progress=progress,
            )
            self._publish_event_sync(message)

        return progress_callback

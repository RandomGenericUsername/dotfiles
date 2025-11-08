"""Pipeline step for setting wallpaper using hyprpaper."""

from dotfiles_pipeline import PipelineContext, PipelineStep
from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.config.config import HyprpaperConfig
from hyprpaper_manager.core.types import MonitorSelector, WallpaperMode

from wallpaper_orchestrator.config.settings import AppConfig
from wallpaper_orchestrator.types import WallpaperResult


class SetWallpaperStep(PipelineStep):
    """Set wallpaper using hyprpaper manager.

    Sets the original wallpaper (not the processed variants) using
    the hyprpaper-manager module.
    """

    @property
    def step_id(self) -> str:
        return "set_wallpaper"

    @property
    def description(self) -> str:
        return "Set wallpaper using hyprpaper"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Execute the wallpaper setting step.

        Args:
            context: Pipeline context containing app_config and wallpaper path

        Returns:
            PipelineContext: Updated context with wallpaper_set status
        """
        config: AppConfig = context.app_config
        result: WallpaperResult = context.results.get("wallpaper_result")

        if not result:
            raise ValueError("No wallpaper_result found in context")

        context.logger_instance.info(
            f"Setting wallpaper: {result.original_wallpaper}"
        )

        # Create hyprpaper config from our settings
        hyprpaper_config = HyprpaperConfig(
            autostart=config.hyprpaper.autostart,
            max_preload_pool_mb=config.hyprpaper.max_preload_pool_mb,
            max_wallpaper_size_multiplier=config.hyprpaper.max_wallpaper_size_multiplier,
            ipc_timeout=config.hyprpaper.ipc_timeout,
            ipc_retry_attempts=config.hyprpaper.ipc_retry_attempts,
            ipc_retry_delay=config.hyprpaper.ipc_retry_delay,
            ipc_startup_wait=config.hyprpaper.ipc_startup_wait,
        )

        # Create manager
        manager = HyprpaperManager(config=hyprpaper_config)

        try:
            # Resolve monitor selector
            monitor = config.hyprpaper.monitor
            if monitor == "all":
                monitor_selector = MonitorSelector.ALL
            elif monitor == "focused":
                monitor_selector = MonitorSelector.FOCUSED
            else:
                monitor_selector = monitor

            # Resolve wallpaper mode
            mode = WallpaperMode(config.hyprpaper.mode)

            context.logger_instance.info(
                f"Monitor: {config.hyprpaper.monitor}"
            )
            context.logger_instance.info(f"Mode: {config.hyprpaper.mode}")

            # Set wallpaper
            manager.set(
                wallpaper=result.original_wallpaper,
                monitor=monitor_selector,
                mode=mode,
            )

            # Update result
            result.wallpaper_set = True
            result.monitor_set = config.hyprpaper.monitor
            context.results["wallpaper_set"] = True

            context.logger_instance.info(
                f"Successfully set wallpaper on {config.hyprpaper.monitor}"
            )

        except Exception as e:
            error_msg = f"Failed to set wallpaper: {e}"
            context.logger_instance.error(error_msg)
            result.errors.append(error_msg)
            result.success = False
            result.wallpaper_set = False
            context.errors.append(e)
            raise

        return context

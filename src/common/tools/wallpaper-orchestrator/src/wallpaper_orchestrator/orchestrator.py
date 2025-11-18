"""Main wallpaper orchestrator."""

from collections.abc import Callable
from pathlib import Path

from dotfiles_logging.rich.rich_logger import RichLogger
from dotfiles_pipeline import Pipeline, PipelineConfig, PipelineContext

from wallpaper_orchestrator.config import AppConfig, load_settings
from wallpaper_orchestrator.steps import (
    GenerateColorSchemeStep,
    GenerateEffectsStep,
    SetWallpaperStep,
)
from wallpaper_orchestrator.types import WallpaperResult


class WallpaperOrchestrator:
    """Orchestrates complete wallpaper setup.

    Coordinates:
    1. Wallpaper effects generation (all variants)
    2. Color scheme generation (from original wallpaper)
    3. Wallpaper setting (using hyprpaper)

    Example:
        >>> from pathlib import Path
        >>> from wallpaper_orchestrator import WallpaperOrchestrator
        >>>
        >>> orchestrator = WallpaperOrchestrator()
        >>> result = orchestrator.process(Path("wallpaper.png"))
        >>>
        >>> print(f"Effects: {len(result.effect_variants)}")
        >>> print(f"Color schemes: {len(result.colorscheme_files)}")
        >>> print(f"Wallpaper set: {result.wallpaper_set}")
    """

    def __init__(
        self,
        config: AppConfig | None = None,
        logger: RichLogger | None = None,
        progress_callback: (
            Callable[[int, int, str, float], None] | None
        ) = None,
        socket_dir: str | Path | None = None,
    ):
        """Initialize orchestrator.

        Args:
            config: Application configuration (loads from settings.toml)
            logger: Logger instance (creates one if None)
            progress_callback: Optional callback for progress updates.
                Signature: (step_index, total_steps, step_name,
                progress_percent)
            socket_dir: Directory for socket file (optional)
        """
        self.config = config or load_settings()
        self._progress_callback = progress_callback
        self._pipeline: Pipeline | None = None

        # Initialize socket manager for real-time progress updates
        from wallpaper_orchestrator.socket_manager import (
            WallpaperProgressSocketManager,
        )

        self.socket_manager = WallpaperProgressSocketManager(
            socket_dir=socket_dir
        )

        # Create logger if not provided
        if logger is None:
            from dotfiles_logging import ConsoleHandlers, Log, LogLevels
            from dotfiles_logging.handlers import RichHandlerSettings

            # Map string log level to LogLevels enum
            log_level_map = {
                "DEBUG": LogLevels.DEBUG,
                "INFO": LogLevels.INFO,
                "WARNING": LogLevels.WARNING,
                "ERROR": LogLevels.ERROR,
                "CRITICAL": LogLevels.CRITICAL,
            }
            log_level = log_level_map.get(
                self.config.orchestrator.log_level.upper(), LogLevels.INFO
            )

            self.logger = Log.create_logger(
                name="wallpaper-orchestrator",
                log_level=log_level,
                console_handler_type=ConsoleHandlers.RICH,
                handler_config=RichHandlerSettings(
                    show_time=True,
                    show_path=False,
                    markup=True,
                ),
            )
        else:
            self.logger = logger

        # Initialize cache manager (if caching is enabled)
        self.cache_manager = None
        if self.config.cache.enabled:
            from dotfiles_state_manager import (
                SQLiteBackend,
                StateManager,
            )

            from wallpaper_orchestrator.cache import WallpaperCacheManager

            # Create state manager with SQLite backend
            backend = SQLiteBackend(
                db_path=self.config.cache.state_manager.db_path
            )
            state_manager = StateManager(backend=backend)

            # Create cache manager
            self.cache_manager = WallpaperCacheManager(
                state_manager=state_manager,
                effects_base_dir=self.config.orchestrator.effects_output_dir,
                colorscheme_cache_dir=self.config.cache.colorscheme_cache_dir,
                colorscheme_active_dir=self.config.orchestrator.colorscheme_output_dir,
            )

    def get_status(self) -> dict[str, float | str | bool | None]:
        """Return current progress status.

        Returns:
            dict with keys:
            - progress: float (0-100)
            - current_step: str | None
            - is_running: bool
        """
        if self._pipeline is None:
            return {
                "progress": 0.0,
                "current_step": None,
                "is_running": False,
            }
        return self._pipeline.get_status()

    def is_running(self) -> bool:
        """Return True if orchestrator is currently processing."""
        if self._pipeline is None:
            return False
        return self._pipeline.is_running()

    def get_current_step(self) -> str | None:
        """Return name of current step or None."""
        if self._pipeline is None:
            return None
        return self._pipeline.get_current_step()

    def process(
        self,
        wallpaper_path: Path,
        effects_output_dir: Path | None = None,
        colorscheme_output_dir: Path | None = None,
        monitor: str | None = None,
        force_rebuild: bool = False,
        generate_colorscheme: bool = True,
        generate_effects: bool = True,
    ) -> WallpaperResult:
        """Process wallpaper: generate effects, colorscheme, set wallpaper.

        Args:
            wallpaper_path: Path to wallpaper image
            effects_output_dir: Output directory for effects (config default)
            colorscheme_output_dir: Output directory for colorscheme
                (config default)
            monitor: Monitor to set wallpaper on (config default)
            force_rebuild: Force regeneration even if cached
            generate_colorscheme: Whether to generate colorscheme
                (default: True)
            generate_effects: Whether to generate effects (default: True)

        Returns:
            WallpaperResult: Complete result metadata with all paths

        Raises:
            FileNotFoundError: If wallpaper file doesn't exist
            Exception: If any pipeline step fails
        """
        # Validate input
        if not wallpaper_path.exists():
            raise FileNotFoundError(f"Wallpaper not found: {wallpaper_path}")

        # Resolve output directories
        if effects_output_dir is None:
            effects_output_dir = self.config.orchestrator.effects_output_dir
        if colorscheme_output_dir is None:
            colorscheme_output_dir = (
                self.config.orchestrator.colorscheme_output_dir
            )

        # Override monitor if provided
        if monitor is not None:
            self.config.hyprpaper.monitor = monitor

        self.logger.info("=" * 60)
        self.logger.info("Wallpaper Orchestration")
        self.logger.info("=" * 60)
        self.logger.info(f"Wallpaper: {wallpaper_path}")
        self.logger.info(f"Effects output: {effects_output_dir}")
        self.logger.info(f"Colorscheme output: {colorscheme_output_dir}")
        self.logger.info("=" * 60)

        # Create result object
        result = WallpaperResult(
            original_wallpaper=wallpaper_path,
            effects_output_dir=effects_output_dir,
            colorscheme_output_dir=colorscheme_output_dir,
        )

        # Create pipeline context
        context = PipelineContext(
            app_config=self.config,
            logger_instance=self.logger,
        )
        context.results["wallpaper_result"] = result

        # Create pipeline configuration
        pipeline_config = PipelineConfig(
            fail_fast=self.config.pipeline.fail_fast,
        )

        # Define pipeline steps (conditionally add generation steps)
        # Pass cache_manager and force_rebuild to steps to avoid deep
        # copy issues
        steps = []

        # Build parallel generation group (if any generation is enabled)
        parallel_group = []
        if generate_colorscheme:
            parallel_group.append(
                GenerateColorSchemeStep(self.cache_manager, force_rebuild)
            )
        if generate_effects:
            parallel_group.append(
                GenerateEffectsStep(self.cache_manager, force_rebuild)
            )

        # Add parallel group if it has any steps
        if parallel_group:
            steps.append(parallel_group)

        # Always add wallpaper setting step
        steps.append(SetWallpaperStep())

        # Create progress callback that sends updates via socket
        def socket_progress_callback(
            step_index: int, total_steps: int, step_name: str, progress: float
        ) -> None:
            """Send progress updates via socket."""
            self.socket_manager.send_progress(
                step_name=step_name,
                progress_percent=progress,
                status="processing",
                extra_data={
                    "step_index": step_index,
                    "total_steps": total_steps,
                },
            )
            # Also call user-provided callback if present
            if self._progress_callback:
                self._progress_callback(
                    step_index, total_steps, step_name, progress
                )

        # Create and run pipeline with socket-enabled progress callback
        self._pipeline = Pipeline(
            steps, pipeline_config, socket_progress_callback
        )

        # Start socket server and run pipeline
        with self.socket_manager:
            try:
                final_context = self._pipeline.run(context)

                # Check for errors
                if final_context.errors:
                    result.success = False
                    error_count = len(final_context.errors)
                    error_msg = f"Pipeline completed with {error_count} errors"
                    self.logger.error(error_msg)
                    # Send error via socket
                    self.socket_manager.send_error(error_msg)
                else:
                    result.success = True
                    self.logger.info("=" * 60)
                    self.logger.info("✓ Wallpaper Orchestration Complete")
                    self.logger.info("=" * 60)
                    # Send completion message
                    self.socket_manager.send_progress(
                        step_name="complete",
                        progress_percent=100.0,
                        status="complete",
                    )

            except Exception as e:
                result.success = False
                error_msg = f"Pipeline failed: {e}"
                result.errors.append(error_msg)
                self.logger.error(error_msg)
                # Send error via socket
                self.socket_manager.send_error(error_msg)
                raise
            finally:
                # Clear pipeline reference after execution
                self._pipeline = None

        return result

    def process_batch(
        self,
        wallpaper_paths: list[Path],
        effects_output_dir: Path | None = None,
        colorscheme_output_dir: Path | None = None,
        monitor: str | None = None,
        force_rebuild: bool = False,
        continue_on_error: bool = True,
        generate_colorscheme: bool = True,
        generate_effects: bool = True,
    ) -> list[WallpaperResult]:
        """Process multiple wallpapers.

        Args:
            wallpaper_paths: List of wallpaper paths
            effects_output_dir: Output directory for effects
            colorscheme_output_dir: Output directory for color schemes
            monitor: Monitor to set wallpaper on
            force_rebuild: Force regeneration even if cached
            continue_on_error: Continue processing if one fails
            generate_colorscheme: Whether to generate colorscheme
                (default: True)
            generate_effects: Whether to generate effects (default: True)

        Returns:
            list[WallpaperResult]: Results for each wallpaper
        """
        results = []

        for wallpaper_path in wallpaper_paths:
            try:
                result = self.process(
                    wallpaper_path=wallpaper_path,
                    effects_output_dir=effects_output_dir,
                    colorscheme_output_dir=colorscheme_output_dir,
                    monitor=monitor,
                    force_rebuild=force_rebuild,
                    generate_colorscheme=generate_colorscheme,
                    generate_effects=generate_effects,
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {wallpaper_path}: {e}")
                if not continue_on_error:
                    raise
                # Create failed result
                failed_result = WallpaperResult(
                    original_wallpaper=wallpaper_path,
                    effects_output_dir=effects_output_dir
                    or self.config.orchestrator.effects_output_dir,
                    colorscheme_output_dir=colorscheme_output_dir
                    or self.config.orchestrator.colorscheme_output_dir,
                    success=False,
                    errors=[str(e)],
                )
                results.append(failed_result)

        return results

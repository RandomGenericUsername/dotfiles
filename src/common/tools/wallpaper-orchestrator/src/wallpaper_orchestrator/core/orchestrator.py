"""Main wallpaper orchestrator."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from dotfiles_logging.rich.rich_logger import RichLogger
from dotfiles_pipeline import Pipeline, PipelineConfig, PipelineContext

from wallpaper_orchestrator.config import AppConfig, load_settings
from wallpaper_orchestrator.core.types import WallpaperResult
from wallpaper_orchestrator.pipeline import (
    GenerateColorSchemeStep,
    GenerateEffectsStep,
    SetWallpaperStep,
)


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

        # Initialize components
        self.socket_manager = self._create_socket_manager(socket_dir)
        self.logger = logger or self._create_logger()
        self.cache_manager = self._create_cache_manager()

    def _create_socket_manager(self, socket_dir: str | Path | None) -> Any:
        """Create socket manager for real-time progress updates.

        Args:
            socket_dir: Directory for socket file (optional)

        Returns:
            WallpaperProgressSocketManager instance
        """
        from wallpaper_orchestrator.integrations import (
            WallpaperProgressSocketManager,
        )

        return WallpaperProgressSocketManager(socket_dir=socket_dir)

    def _create_logger(self) -> RichLogger:
        """Create logger with configuration from settings.

        Returns:
            RichLogger instance configured for wallpaper orchestrator
        """
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

        return Log.create_logger(
            name="wallpaper-orchestrator",
            log_level=log_level,
            console_handler_type=ConsoleHandlers.RICH,
            handler_config=RichHandlerSettings(
                show_time=True,
                show_path=False,
                markup=True,
            ),
        )

    def _create_cache_manager(self) -> Any:
        """Create cache manager if caching is enabled.

        Returns:
            WallpaperCacheManager instance or None if caching disabled
        """
        if not self.config.cache.enabled:
            return None

        from dotfiles_state_manager import SQLiteBackend, StateManager

        from wallpaper_orchestrator.core.cache import WallpaperCacheManager

        # Create state manager with SQLite backend
        backend = SQLiteBackend(
            db_path=self.config.cache.state_manager.db_path
        )
        state_manager = StateManager(backend=backend)

        # Create cache manager
        return WallpaperCacheManager(
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

    def _validate_wallpaper(self, wallpaper_path: Path) -> None:
        """Validate that wallpaper file exists.

        Args:
            wallpaper_path: Path to wallpaper image

        Raises:
            FileNotFoundError: If wallpaper file doesn't exist
        """
        if not wallpaper_path.exists():
            raise FileNotFoundError(f"Wallpaper not found: {wallpaper_path}")

    def _resolve_output_directories(
        self,
        effects_output_dir: Path | None,
        colorscheme_output_dir: Path | None,
    ) -> tuple[Path, Path]:
        """Resolve output directories using config defaults if not provided.

        Args:
            effects_output_dir: Output directory for effects (optional)
            colorscheme_output_dir: Output directory for colorscheme (optional)

        Returns:
            Tuple of (effects_output_dir, colorscheme_output_dir)
        """
        if effects_output_dir is None:
            effects_output_dir = self.config.orchestrator.effects_output_dir
        if colorscheme_output_dir is None:
            colorscheme_output_dir = (
                self.config.orchestrator.colorscheme_output_dir
            )
        return effects_output_dir, colorscheme_output_dir

    def _apply_monitor_override(self, monitor: str | None) -> None:
        """Apply monitor override to configuration if provided.

        Args:
            monitor: Monitor to set wallpaper on (optional)
        """
        if monitor is not None:
            self.config.hyprpaper.monitor = monitor

    def _log_orchestration_start(
        self,
        wallpaper_path: Path,
        effects_output_dir: Path,
        colorscheme_output_dir: Path,
    ) -> None:
        """Log orchestration start with configuration details.

        Args:
            wallpaper_path: Path to wallpaper image
            effects_output_dir: Output directory for effects
            colorscheme_output_dir: Output directory for colorscheme
        """
        self.logger.info("=" * 60)
        self.logger.info("Wallpaper Orchestration")
        self.logger.info("=" * 60)
        self.logger.info(f"Wallpaper: {wallpaper_path}")
        self.logger.info(f"Effects output: {effects_output_dir}")
        self.logger.info(f"Colorscheme output: {colorscheme_output_dir}")
        self.logger.info("=" * 60)

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
        self._validate_wallpaper(wallpaper_path)

        # Resolve configuration
        effects_output_dir, colorscheme_output_dir = (
            self._resolve_output_directories(
                effects_output_dir, colorscheme_output_dir
            )
        )
        self._apply_monitor_override(monitor)

        # Log start
        self._log_orchestration_start(
            wallpaper_path, effects_output_dir, colorscheme_output_dir
        )

        # Create result and context
        result = self._create_result_object(
            wallpaper_path, effects_output_dir, colorscheme_output_dir
        )
        context = self._create_pipeline_context(result)

        # Build and execute pipeline
        steps = self._build_pipeline_steps(
            generate_colorscheme, generate_effects, force_rebuild
        )
        pipeline = self._create_pipeline(steps, wallpaper_path)

        # Execute with socket management
        return self._execute_pipeline(pipeline, context, result)

    def _create_result_object(
        self,
        wallpaper_path: Path,
        effects_output_dir: Path,
        colorscheme_output_dir: Path,
    ) -> WallpaperResult:
        """Create result object to track orchestration results.

        Args:
            wallpaper_path: Path to wallpaper image
            effects_output_dir: Output directory for effects
            colorscheme_output_dir: Output directory for colorscheme

        Returns:
            WallpaperResult instance
        """
        return WallpaperResult(
            original_wallpaper=wallpaper_path,
            effects_output_dir=effects_output_dir,
            colorscheme_output_dir=colorscheme_output_dir,
        )

    def _create_pipeline_context(
        self, result: WallpaperResult
    ) -> PipelineContext:
        """Create pipeline context with configuration and result.

        Args:
            result: WallpaperResult instance to track in context

        Returns:
            PipelineContext instance
        """
        context = PipelineContext(
            app_config=self.config,
            logger_instance=self.logger,
        )
        context.results["wallpaper_result"] = result
        return context

    def _build_pipeline_steps(
        self,
        generate_colorscheme: bool,
        generate_effects: bool,
        force_rebuild: bool,
    ) -> list:
        """Build list of pipeline steps based on configuration.

        Args:
            generate_colorscheme: Whether to generate colorscheme
            generate_effects: Whether to generate effects
            force_rebuild: Whether to force rebuild even if cached

        Returns:
            List of pipeline steps (may include nested parallel groups)
        """
        steps = []

        # Build parallel generation group (if any generation is enabled)
        parallel_group = self._build_parallel_generation_group(
            generate_colorscheme, generate_effects, force_rebuild
        )

        # Add parallel group if it has any steps
        if parallel_group:
            steps.append(parallel_group)

        # Always add wallpaper setting step
        steps.append(SetWallpaperStep())

        return steps

    def _build_parallel_generation_group(
        self,
        generate_colorscheme: bool,
        generate_effects: bool,
        force_rebuild: bool,
    ) -> list:
        """Build parallel generation group for colorscheme and effects.

        Args:
            generate_colorscheme: Whether to generate colorscheme
            generate_effects: Whether to generate effects
            force_rebuild: Whether to force rebuild even if cached

        Returns:
            List of steps to run in parallel (may be empty)
        """
        parallel_group = []

        if generate_colorscheme:
            parallel_group.append(
                GenerateColorSchemeStep(self.cache_manager, force_rebuild)
            )
        if generate_effects:
            parallel_group.append(
                GenerateEffectsStep(self.cache_manager, force_rebuild)
            )

        return parallel_group

    def _map_step_name_to_display_name(self, step_name: str) -> str:
        """Map internal step names to user-friendly display names.

        Args:
            step_name: Internal step name from pipeline

        Returns:
            User-friendly display name
        """
        step_name_map = {
            "parallel_group_0": "Processing colorscheme & effects",
            "generate_colorscheme": "Generating colorscheme",
            "generate_effects": "Creating effect variants",
            "set_wallpaper": "Setting wallpaper",
        }
        return step_name_map.get(step_name, step_name)

    def _create_progress_callback(
        self, wallpaper_path: Path
    ) -> Callable[[int, int, str, float], None]:
        """Create progress callback that sends updates via socket.

        Args:
            wallpaper_path: Path to wallpaper being processed

        Returns:
            Progress callback function
        """

        def socket_progress_callback(
            step_index: int, total_steps: int, step_name: str, progress: float
        ) -> None:
            """Send progress updates via socket."""
            display_name = self._map_step_name_to_display_name(step_name)

            self.socket_manager.send_progress(
                step_name=display_name,
                progress_percent=progress,
                status="processing",
                extra_data={
                    "step_index": step_index,
                    "total_steps": total_steps,
                    "wallpaper_path": str(wallpaper_path),
                },
            )
            # Also call user-provided callback if present
            if self._progress_callback:
                self._progress_callback(
                    step_index, total_steps, step_name, progress
                )

        return socket_progress_callback

    def _create_pipeline(self, steps: list, wallpaper_path: Path) -> Pipeline:
        """Create pipeline with steps and progress callback.

        Args:
            steps: List of pipeline steps
            wallpaper_path: Path to wallpaper being processed

        Returns:
            Pipeline instance
        """
        pipeline_config = PipelineConfig(
            fail_fast=self.config.pipeline.fail_fast,
        )
        progress_callback = self._create_progress_callback(wallpaper_path)

        return Pipeline(steps, pipeline_config, progress_callback)

    def _execute_pipeline(
        self,
        pipeline: Pipeline,
        context: PipelineContext,
        result: WallpaperResult,
    ) -> WallpaperResult:
        """Execute pipeline with socket management and error handling.

        Args:
            pipeline: Pipeline to execute
            context: Pipeline context
            result: Result object to update

        Returns:
            Updated WallpaperResult

        Raises:
            Exception: If pipeline execution fails
        """
        self._pipeline = pipeline

        # Start socket server and run pipeline
        with self.socket_manager:
            try:
                final_context = self._pipeline.run(context)

                # Check for errors
                if final_context.errors:
                    self._handle_pipeline_errors(result, final_context)
                else:
                    self._handle_pipeline_success(
                        result, result.original_wallpaper
                    )

            except Exception as e:
                self._handle_pipeline_exception(result, e)
                raise
            finally:
                # Clear pipeline reference after execution
                self._pipeline = None

        return result

    def _handle_pipeline_errors(
        self, result: WallpaperResult, context: PipelineContext
    ) -> None:
        """Handle pipeline errors.

        Args:
            result: Result object to update
            context: Pipeline context with errors
        """
        result.success = False
        error_count = len(context.errors)
        error_msg = f"Pipeline completed with {error_count} errors"
        self.logger.error(error_msg)
        self.socket_manager.send_error(error_msg)

    def _handle_pipeline_success(
        self, result: WallpaperResult, wallpaper_path: Path
    ) -> None:
        """Handle successful pipeline completion.

        Args:
            result: Result object to update
            wallpaper_path: Path to wallpaper that was processed
        """
        result.success = True
        self.logger.info("=" * 60)
        self.logger.info("✓ Wallpaper Orchestration Complete")
        self.logger.info("=" * 60)

        # Send completion message
        self.socket_manager.send_progress(
            step_name="Wallpaper changed successfully",
            progress_percent=100.0,
            status="completed",
            extra_data={"wallpaper_path": str(wallpaper_path)},
        )

    def _handle_pipeline_exception(
        self, result: WallpaperResult, exception: Exception
    ) -> None:
        """Handle pipeline exception.

        Args:
            result: Result object to update
            exception: Exception that was raised
        """
        result.success = False
        error_msg = f"Pipeline failed: {exception}"
        result.errors.append(error_msg)
        self.logger.error(error_msg)
        self.socket_manager.send_error(error_msg)

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

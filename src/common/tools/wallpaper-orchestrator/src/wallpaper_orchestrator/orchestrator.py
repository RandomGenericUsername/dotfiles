"""Main wallpaper orchestrator."""

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
    ):
        """Initialize orchestrator.

        Args:
            config: Application configuration (loads from settings.toml if None)
            logger: Logger instance (creates one if None)
        """
        self.config = config or load_settings()

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

    def process(
        self,
        wallpaper_path: Path,
        effects_output_dir: Path | None = None,
        colorscheme_output_dir: Path | None = None,
        monitor: str | None = None,
    ) -> WallpaperResult:
        """Process wallpaper: generate effects, color scheme, and set wallpaper.

        Args:
            wallpaper_path: Path to wallpaper image
            effects_output_dir: Output directory for effects (uses config default if None)
            colorscheme_output_dir: Output directory for color schemes (uses config default if None)
            monitor: Monitor to set wallpaper on (uses config default if None)

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

        # Define pipeline steps (all serial)
        steps = [
            GenerateEffectsStep(),
            GenerateColorSchemeStep(),
            SetWallpaperStep(),
        ]

        # Create and run pipeline
        pipeline = Pipeline(steps, pipeline_config)

        try:
            final_context = pipeline.run(context)

            # Check for errors
            if final_context.errors:
                result.success = False
                self.logger.error(
                    f"Pipeline completed with {len(final_context.errors)} errors"
                )
            else:
                result.success = True
                self.logger.info("=" * 60)
                self.logger.info("✓ Wallpaper Orchestration Complete")
                self.logger.info("=" * 60)

        except Exception as e:
            result.success = False
            error_msg = f"Pipeline failed: {e}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
            raise

        return result

    def process_batch(
        self,
        wallpaper_paths: list[Path],
        effects_output_dir: Path | None = None,
        colorscheme_output_dir: Path | None = None,
        monitor: str | None = None,
        continue_on_error: bool = True,
    ) -> list[WallpaperResult]:
        """Process multiple wallpapers.

        Args:
            wallpaper_paths: List of wallpaper paths
            effects_output_dir: Output directory for effects
            colorscheme_output_dir: Output directory for color schemes
            monitor: Monitor to set wallpaper on
            continue_on_error: Continue processing if one fails

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

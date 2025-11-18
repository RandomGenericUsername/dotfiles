"""Pipeline step for generating color scheme from wallpaper."""

from colorscheme_orchestrator import ColorSchemeOrchestrator
from dotfiles_pipeline import PipelineContext, PipelineStep

from wallpaper_orchestrator.config.settings import AppConfig
from wallpaper_orchestrator.types import WallpaperResult
from wallpaper_orchestrator.utils.sequences import send_sequences_to_terminals


class GenerateColorSchemeStep(PipelineStep):
    """Generate color scheme from original wallpaper.

    Uses the colorscheme-orchestrator to generate color scheme files
    from the original wallpaper (not the processed variants).
    """

    def __init__(self, cache_manager=None, force_rebuild: bool = False):
        """Initialize step with cache manager and force_rebuild flag.

        Args:
            cache_manager: Cache manager instance (optional)
            force_rebuild: Whether to force rebuild even if cached
        """
        self.cache_manager = cache_manager
        self.force_rebuild = force_rebuild

    @property
    def step_id(self) -> str:
        return "generate_colorscheme"

    @property
    def description(self) -> str:
        return "Generate color scheme from wallpaper"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Execute the color scheme generation step with caching.

        Args:
            context: Pipeline context containing app_config and wallpaper path

        Returns:
            PipelineContext: Updated context with colorscheme_files in results
        """
        config: AppConfig = context.app_config
        result: WallpaperResult = context.results.get("wallpaper_result")

        if not result:
            raise ValueError("No wallpaper_result found in context")

        # Use cache manager and force_rebuild from instance attributes
        cache_manager = self.cache_manager
        force_rebuild = self.force_rebuild

        expected_formats = config.colorscheme.formats

        # Check cache first (if enabled and cache manager available)
        if (
            cache_manager
            and config.cache.enabled
            and not force_rebuild
            and cache_manager.is_colorscheme_cached(
                result.original_wallpaper, expected_formats
            )
        ):
            context.logger_instance.info(
                "✓ Colorscheme already cached, restoring to active location"
            )

            # Restore cached colorscheme to active directory
            colorscheme_files = cache_manager.restore_colorscheme_to_active(
                result.original_wallpaper, expected_formats
            )

            result.colorscheme_files = colorscheme_files
            result.colorscheme_generated = (
                True  # Mark as generated (from cache)
            )
            context.results["colorscheme_files"] = colorscheme_files

            context.logger_instance.info(
                f"  Restored {len(colorscheme_files)} colorscheme files"
            )

            # Send sequences to all open terminals for instant color update
            if "sequences" in colorscheme_files:
                sequences_file = colorscheme_files["sequences"]
                successful, failed = send_sequences_to_terminals(
                    sequences_file
                )
                if successful > 0:
                    context.logger_instance.debug(
                        f"  Sent color sequences to {successful} terminal(s)"
                    )
                if failed > 0:
                    context.logger_instance.debug(
                        f"  Failed to send sequences to {failed} terminal(s)"
                    )

            return context

        # Generate colorscheme (cache miss or disabled)
        context.logger_instance.info(
            f"Generating color scheme from: {result.original_wallpaper}"
        )

        # Create orchestrator with default config
        orchestrator = ColorSchemeOrchestrator()

        # Report initial progress
        context.update_step_progress(0.0)

        try:
            # Determine output directory:
            # - If caching enabled: generate directly to per-wallpaper cache
            # - If caching disabled: generate to shared active directory
            if cache_manager and config.cache.enabled:
                # Generate to per-wallpaper cache directory
                wallpaper_subdir = result.original_wallpaper.stem
                output_dir = (
                    config.cache.colorscheme_cache_dir / wallpaper_subdir
                )
            else:
                # Generate to shared active directory
                output_dir = result.colorscheme_output_dir

            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate color scheme
            context.logger_instance.info(
                f"Backend: {config.colorscheme.backend}"
            )
            context.logger_instance.info(f"Output directory: {output_dir}")
            context.logger_instance.info(
                f"Formats: {', '.join(config.colorscheme.formats)}"
            )

            colorscheme_files = orchestrator.generate(
                backend=config.colorscheme.backend,
                image_path=result.original_wallpaper,
                output_dir=output_dir,
                formats=config.colorscheme.formats,
                color_count=config.colorscheme.color_count,
                rebuild=False,
                keep_container=False,
                progress_callback=context.update_step_progress,
            )

            # If caching enabled, activate the colorscheme and mark as cached
            if cache_manager and config.cache.enabled:
                # Activate the colorscheme (copy to active directory)
                active_files = cache_manager.activate_colorscheme(
                    result.original_wallpaper, colorscheme_files
                )
                context.logger_instance.debug("  Activated colorscheme")

                # Mark as cached
                cache_manager.mark_colorscheme_cached(
                    result.original_wallpaper,
                    colorscheme_files,
                )
                context.logger_instance.debug("  Marked colorscheme as cached")

                # Send sequences to all open terminals for instant color update
                if "sequences" in active_files:
                    sequences_file = active_files["sequences"]
                    successful, failed = send_sequences_to_terminals(
                        sequences_file
                    )
                    if successful > 0:
                        context.logger_instance.debug(
                            f"  Sent color sequences to {successful} "
                            f"terminal(s)"
                        )
                    if failed > 0:
                        context.logger_instance.debug(
                            f"  Failed to send sequences to {failed} "
                            f"terminal(s)"
                        )

            # Store results
            result.colorscheme_files = colorscheme_files
            result.colorscheme_generated = True  # Mark as generated (fresh)
            context.results["colorscheme_files"] = colorscheme_files

            context.logger_instance.info(
                f"Generated {len(colorscheme_files)} color scheme files"
            )

            for fmt, path in colorscheme_files.items():
                context.logger_instance.debug(f"  • {fmt}: {path}")

        except Exception as e:
            error_msg = f"Failed to generate color scheme: {e}"
            context.logger_instance.error(error_msg)
            result.errors.append(error_msg)
            result.success = False
            context.errors.append(e)
            raise

        return context

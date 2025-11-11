"""Pipeline step for generating color scheme from wallpaper."""

from colorscheme_orchestrator import ColorSchemeOrchestrator
from dotfiles_pipeline import PipelineContext, PipelineStep

from wallpaper_orchestrator.config.settings import AppConfig
from wallpaper_orchestrator.types import WallpaperResult


class GenerateColorSchemeStep(PipelineStep):
    """Generate color scheme from original wallpaper.

    Uses the colorscheme-orchestrator to generate color scheme files
    from the original wallpaper (not the processed variants).
    """

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

        # Get cache manager and force_rebuild flag from context
        cache_manager = context.results.get("cache_manager")
        force_rebuild = context.results.get("force_rebuild", False)

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
            context.results["colorscheme_files"] = colorscheme_files

            context.logger_instance.info(
                f"  Restored {len(colorscheme_files)} colorscheme files"
            )
            return context

        # Generate colorscheme (cache miss or disabled)
        context.logger_instance.info(
            f"Generating color scheme from: {result.original_wallpaper}"
        )

        # Create orchestrator with default config
        orchestrator = ColorSchemeOrchestrator()

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
            )

            # If caching enabled, activate the colorscheme and mark as cached
            if cache_manager and config.cache.enabled:
                # Activate the colorscheme (copy to active directory)
                cache_manager.activate_colorscheme(
                    result.original_wallpaper, colorscheme_files
                )
                context.logger_instance.debug("  Activated colorscheme")

                # Mark as cached
                cache_manager.mark_colorscheme_cached(
                    result.original_wallpaper,
                    colorscheme_files,
                )
                context.logger_instance.debug("  Marked colorscheme as cached")

            # Store results
            result.colorscheme_files = colorscheme_files
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

"""Pipeline step for generating wallpaper effect variants."""

from dotfiles_pipeline import PipelineContext, PipelineStep
from wallpaper_effects_orchestrator import (
    WallpaperOrchestrator as EffectsOrchestrator,
)
from wallpaper_effects_orchestrator import (
    get_default_config as get_effects_config,
)

from wallpaper_orchestrator.config.settings import AppConfig
from wallpaper_orchestrator.core.types import WallpaperResult


class GenerateEffectsStep(PipelineStep):
    """Generate all wallpaper effect variants.

    Uses the wallpaper-effects-orchestrator to generate all available
    effect variants from the original wallpaper.
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
        return "generate_effects"

    @property
    def description(self) -> str:
        return "Generate wallpaper effect variants"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Execute the effects generation step with caching.

        Args:
            context: Pipeline context containing app_config and wallpaper path

        Returns:
            PipelineContext: Updated context with effect_variants in results
        """
        config: AppConfig = context.app_config
        result: WallpaperResult = context.results.get("wallpaper_result")

        if not result:
            raise ValueError("No wallpaper_result found in context")

        # Use cache manager and force_rebuild from instance attributes
        cache_manager = self.cache_manager
        force_rebuild = self.force_rebuild

        # Get expected effects from processor
        from wallpaper_processor.factory import EffectFactory

        expected_effects = EffectFactory.get_all_effect_names()

        # Check cache first (if enabled and cache manager available)
        if (
            cache_manager
            and config.cache.enabled
            and not force_rebuild
            and cache_manager.is_effects_cached(
                result.original_wallpaper, expected_effects
            )
        ):
            context.logger_instance.info(
                "✓ Effects already cached, skipping generation"
            )

            # Get cached effect paths
            cached_variants = cache_manager.get_cached_effects(
                result.original_wallpaper, expected_effects
            )

            result.effect_variants = cached_variants
            result.effects_generated = True  # Mark as generated (from cache)
            context.results["effect_variants"] = cached_variants

            context.logger_instance.info(
                f"  Loaded {len(cached_variants)} cached variants"
            )
            return context

        # Generate effects (cache miss or disabled)
        context.logger_instance.info(
            f"Generating effect variants for: {result.original_wallpaper}"
        )

        # Load default config and override with our settings
        effects_config = get_effects_config()
        effects_config.container.runtime = (
            config.wallpaper_effects.container_runtime
        )
        effects_config.container.image_name = (
            config.wallpaper_effects.image_name
        )
        effects_config.container.image_tag = config.wallpaper_effects.image_tag

        # Create orchestrator
        orchestrator = EffectsOrchestrator(effects_config)

        # Report initial progress
        context.update_step_progress(0.0)

        try:
            # Ensure output directory exists
            result.effects_output_dir.mkdir(parents=True, exist_ok=True)

            # Ensure image exists
            context.logger_instance.info("Ensuring container image exists...")
            orchestrator.ensure_image()

            # Generate all effect variants
            context.logger_instance.info(
                f"Output directory: {result.effects_output_dir}"
            )

            effect_variants = orchestrator.generate_all_variants(
                input_path=result.original_wallpaper,
                output_dir=result.effects_output_dir,
                progress_callback=context.update_step_progress,
            )

            # Mark as cached (if cache manager available)
            if cache_manager and config.cache.enabled:
                effects_dir = (
                    result.effects_output_dir / result.original_wallpaper.stem
                )
                cache_manager.mark_effects_cached(
                    result.original_wallpaper,
                    effects_dir,
                    effect_variants,
                )
                context.logger_instance.debug("  Marked effects as cached")

            # Store results
            result.effect_variants = effect_variants
            result.effects_generated = True  # Mark as generated (fresh)
            context.results["effect_variants"] = effect_variants

            context.logger_instance.info(
                f"Generated {len(effect_variants)} effect variants"
            )

            for effect_name, path in effect_variants.items():
                context.logger_instance.debug(f"  • {effect_name}: {path}")

        except Exception as e:
            error_msg = f"Failed to generate effect variants: {e}"
            context.logger_instance.error(error_msg)
            result.errors.append(error_msg)
            result.success = False
            context.errors.append(e)
            raise

        return context

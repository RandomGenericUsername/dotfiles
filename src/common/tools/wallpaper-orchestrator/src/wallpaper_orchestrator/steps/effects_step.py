"""Pipeline step for generating wallpaper effect variants."""

from dotfiles_pipeline import PipelineContext, PipelineStep
from wallpaper_effects_orchestrator import (
    WallpaperOrchestrator as EffectsOrchestrator,
)
from wallpaper_effects_orchestrator import (
    get_default_config as get_effects_config,
)

from wallpaper_orchestrator.config.settings import AppConfig
from wallpaper_orchestrator.types import WallpaperResult


class GenerateEffectsStep(PipelineStep):
    """Generate all wallpaper effect variants.

    Uses the wallpaper-effects-orchestrator to generate all available
    effect variants from the original wallpaper.
    """

    @property
    def step_id(self) -> str:
        return "generate_effects"

    @property
    def description(self) -> str:
        return "Generate wallpaper effect variants"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Execute the effects generation step.

        Args:
            context: Pipeline context containing app_config and wallpaper path

        Returns:
            PipelineContext: Updated context with effect_variants in results
        """
        config: AppConfig = context.app_config
        result: WallpaperResult = context.results.get("wallpaper_result")

        if not result:
            raise ValueError("No wallpaper_result found in context")

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
            )

            # Store results
            result.effect_variants = effect_variants
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

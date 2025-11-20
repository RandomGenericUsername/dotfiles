"""Status bar icons hook."""

import json
from pathlib import Path

from icon_generator import IconRegistry, IconService, IconGenerationRequest

from dotfiles_manager.hooks.base import Hook
from dotfiles_manager.models.hook import HookContext, HookResult
from dotfiles_manager.services.svg_template_cache_manager import (
    SVGTemplateCacheManager,
)


class StatusBarIconsHook(Hook):
    """Hook to generate status bar icons after wallpaper change."""

    def __init__(
        self,
        icon_registry: IconRegistry,
        icon_service: IconService,
        icons_output_dir: Path,
        default_variant: str,
        variant_overrides: dict[str, str],
    ):
        """Initialize status bar icons hook.

        Args:
            icon_registry: Icon registry instance
            icon_service: Icon service instance
            icons_output_dir: Directory to write generated icons
            default_variant: Default icon variant for all categories
            variant_overrides: Per-category icon variant overrides
        """
        self._icon_registry = icon_registry
        self._icon_service = icon_service
        self._icons_output_dir = icons_output_dir
        self._default_variant = default_variant
        self._variant_overrides = variant_overrides

    @property
    def name(self) -> str:
        """Unique identifier for this hook."""
        return "status_bar_icons"

    def execute(self, context: HookContext) -> HookResult:
        """Execute hook to generate status bar icons.

        Args:
            context: Hook execution context

        Returns:
            HookResult: Result of hook execution
        """
        try:
            # Skip if colorscheme was not generated
            if not context.colorscheme_generated:
                return HookResult(
                    success=True,
                    message="Skipped (no colorscheme generated)",
                )

            # Get colorscheme color key from config
            color_key = context.config.get("colorscheme_color_key", "color15")

            # Extract color and full colorscheme from JSON
            colorscheme_json_path = context.colorscheme_files.get("json")
            if not colorscheme_json_path or not colorscheme_json_path.exists():
                return HookResult(
                    success=False,
                    message="Colorscheme JSON file not found",
                )

            colorscheme_data = json.loads(colorscheme_json_path.read_text())
            color = colorscheme_data.get("colors", {}).get(color_key, "#ffffff")

            # Generate icons for each category
            total_icons = 0
            total_cache_hits = 0
            total_cache_misses = 0
            categories_processed = []

            for category_name in self._icon_registry.list_categories():
                category = self._icon_registry.get_category(category_name)

                # Determine variant for this category
                variant = self._variant_overrides.get(
                    category_name, self._default_variant
                )

                # Skip variant if category doesn't have variants
                if not category.has_variants:
                    variant = None

                # Create output directory for this category
                category_output_dir = self._icons_output_dir / category_name
                category_output_dir.mkdir(parents=True, exist_ok=True)

                # Generate icons
                request = IconGenerationRequest(
                    category=category_name,
                    variant=variant,
                    color=color,
                    colorscheme_data=colorscheme_data,
                    output_dir=category_output_dir,
                )

                result = self._icon_service.generate_icons(request)

                if result.success:
                    total_icons += result.total_icons
                    total_cache_hits += result.cache_hits
                    total_cache_misses += result.cache_misses
                    categories_processed.append(category_name)

            cache_hit_rate = (
                (total_cache_hits / (total_cache_hits + total_cache_misses) * 100)
                if (total_cache_hits + total_cache_misses) > 0
                else 0
            )

            return HookResult(
                success=True,
                message=(
                    f"Generated {total_icons} icons across {len(categories_processed)} "
                    f"categories (cache hit rate: {cache_hit_rate:.1f}%)"
                ),
                data={
                    "total_icons": total_icons,
                    "categories": categories_processed,
                    "cache_hits": total_cache_hits,
                    "cache_misses": total_cache_misses,
                    "cache_hit_rate": cache_hit_rate,
                },
            )

        except Exception as e:
            return HookResult(
                success=False,
                message=f"Failed to generate status bar icons: {e}",
            )

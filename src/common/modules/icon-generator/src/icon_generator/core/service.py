"""Icon generation service with caching support."""

import logging
from pathlib import Path
from typing import Any, Protocol

from icon_generator.core.registry import IconRegistry
from icon_generator.exceptions import (
    IconGenerationError,
    IconVariantNotFoundError,
)
from icon_generator.models.requests import (
    IconGenerationRequest,
    IconGenerationResult,
)

logger = logging.getLogger(__name__)


class SVGCacheManager(Protocol):
    """Protocol for SVG cache manager."""

    def compute_colorscheme_hash(
        self, colorscheme_data: dict[str, Any]
    ) -> str:
        """Compute hash of colorscheme data."""
        ...

    def get_cached_svg(
        self, colorscheme_hash: str, template_name: str
    ) -> str | None:
        """Get cached SVG content."""
        ...

    def cache_svg(
        self, colorscheme_hash: str, template_name: str, svg_content: str
    ) -> None:
        """Cache SVG content."""
        ...


class SVGRenderer(Protocol):
    """Protocol for SVG template renderer."""

    def render(self, template_path: Path, context: dict[str, Any]) -> str:
        """Render SVG template with context."""
        ...


class IconService:
    """Service for generating icons with template rendering and caching.

    The service uses an IconRegistry to discover available icons, renders
    SVG templates with colorscheme data, and integrates with an optional
    SVG cache manager for performance optimization.
    """

    def __init__(
        self,
        registry: IconRegistry,
        cache_manager: SVGCacheManager | None = None,
        renderer: SVGRenderer | None = None,
    ) -> None:
        """Initialize icon service.

        Args:
            registry: Icon registry for category/variant discovery
            cache_manager: Optional SVG cache manager for performance
            renderer: Optional SVG renderer (if None, uses simple file read)
        """
        self._registry = registry
        self._cache = cache_manager
        self._renderer = renderer

    def generate_icons(
        self, request: IconGenerationRequest
    ) -> IconGenerationResult:
        """Generate icons based on request.

        Args:
            request: Icon generation request

        Returns:
            Icon generation result with statistics

        Raises:
            IconCategoryNotFoundError: If category not found
            IconVariantNotFoundError: If variant not found
        """
        logger.info(
            f"Generating icons for category '{request.category}'"
            + (f" (variant: {request.variant})" if request.variant else "")
        )

        # Get category metadata
        category = self._registry.get_category(request.category)

        # Validate variant
        if category.has_variants:
            if request.variant is None:
                raise ValueError(
                    f"Category '{request.category}' has variants, "
                    f"variant must be specified"
                )
            if request.variant not in category.variants:
                raise IconVariantNotFoundError(
                    request.category,
                    request.variant,
                    category.list_variants(),
                )
        elif request.variant is not None:
            logger.warning(
                f"Category '{request.category}' has no variants, "
                f"ignoring variant '{request.variant}'"
            )

        # Compute colorscheme hash for caching
        colorscheme_hash = None
        if self._cache and request.colorscheme_data:
            colorscheme_hash = self._cache.compute_colorscheme_hash(
                request.colorscheme_data
            )
            logger.debug(f"Colorscheme hash: {colorscheme_hash[:16]}...")

        # Determine which icons to generate
        icons_to_generate = (
            request.icons
            if request.icons
            else category.list_icons(request.variant)
        )

        logger.debug(
            f"Generating {len(icons_to_generate)} icons: "
            f"{', '.join(icons_to_generate[:5])}"
            + ("..." if len(icons_to_generate) > 5 else "")
        )

        # Create output directory
        request.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate icons
        generated_icons: dict[str, Path] = {}
        errors: dict[str, str] = {}
        cache_hits = 0
        cache_misses = 0

        for icon_name in icons_to_generate:
            try:
                output_path, from_cache = self._generate_single_icon(
                    category=category,
                    icon_name=icon_name,
                    variant=request.variant,
                    color=request.color,
                    context=request.context,
                    output_dir=request.output_dir,
                    colorscheme_hash=colorscheme_hash,
                )
                generated_icons[icon_name] = output_path

                if from_cache:
                    cache_hits += 1
                else:
                    cache_misses += 1

            except Exception as e:
                error_msg = str(e)
                errors[icon_name] = error_msg
                logger.error(
                    f"Failed to generate icon '{icon_name}': {error_msg}"
                )

        # Log results
        logger.info(
            f"Generated {len(generated_icons)}/{len(icons_to_generate)} icons"
        )
        if cache_hits > 0 or cache_misses > 0:
            hit_rate = (
                (cache_hits / (cache_hits + cache_misses)) * 100
                if (cache_hits + cache_misses) > 0
                else 0
            )
            logger.info(
                f"Cache: {cache_hits} hits, {cache_misses} misses "
                f"({hit_rate:.1f}% hit rate)"
            )

        return IconGenerationResult(
            category=request.category,
            variant=request.variant,
            generated_icons=generated_icons,
            from_cache=cache_hits > 0,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            errors=errors,
        )

    def _generate_single_icon(
        self,
        category: Any,  # IconCategory
        icon_name: str,
        variant: str | None,
        color: str,
        context: dict[str, Any],
        output_dir: Path,
        colorscheme_hash: str | None,
    ) -> tuple[Path, bool]:
        """Generate a single icon.

        Args:
            category: Icon category metadata
            icon_name: Name of icon to generate
            variant: Variant name or None
            color: Primary color for rendering
            context: Additional template context
            output_dir: Output directory
            colorscheme_hash: Colorscheme hash for caching

        Returns:
            Tuple of (output_path, from_cache)

        Raises:
            IconGenerationError: If generation fails
        """
        # Get template path
        try:
            template_path = category.get_icon_path(icon_name, variant)
        except KeyError as e:
            raise IconGenerationError(
                f"Icon file not found: {e}",
                category.name,
                icon_name,
            ) from e

        if not template_path.exists():
            raise IconGenerationError(
                f"Template file does not exist: {template_path}",
                category.name,
                icon_name,
            )

        # Build hierarchical template name for cache
        if variant:
            template_name = f"{category.name}/{variant}/{icon_name}.svg"
        else:
            template_name = f"{category.name}/{icon_name}.svg"

        # Try to get from cache
        rendered = None
        from_cache = False

        if self._cache and colorscheme_hash:
            rendered = self._cache.get_cached_svg(
                colorscheme_hash, template_name
            )
            if rendered:
                from_cache = True
                logger.debug(f"  Cache hit: {template_name}")

        # Render if not cached
        if rendered is None:
            logger.debug(f"  Rendering: {template_name}")

            # Build template context
            template_context = {
                "CURRENT_COLOR": color,
                **context,
            }

            # Render template
            if self._renderer:
                rendered = self._renderer.render(
                    template_path, template_context
                )
            else:
                # Simple fallback: read file and replace placeholder
                rendered = template_path.read_text()
                for key, value in template_context.items():
                    rendered = rendered.replace(f"{{{{{key}}}}}", str(value))

            # Cache the result
            if self._cache and colorscheme_hash:
                self._cache.cache_svg(
                    colorscheme_hash, template_name, rendered
                )

        # Write to output file
        output_path = output_dir / f"{icon_name}.svg"
        output_path.write_text(rendered)

        return output_path, from_cache

    def get_icon_path(
        self, category: str, variant: str | None, icon_name: str
    ) -> Path:
        """Get path to a generated icon file.

        This is a helper method to get the expected output path for an icon.
        It does not check if the file actually exists.

        Args:
            category: Category name
            variant: Variant name or None
            icon_name: Icon name

        Returns:
            Expected path to icon file

        Raises:
            IconCategoryNotFoundError: If category not found
        """
        cat = self._registry.get_category(category)
        return cat.get_icon_path(icon_name, variant)

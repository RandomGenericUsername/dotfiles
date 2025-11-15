"""Wlogout service for generating icons and styles."""

from pathlib import Path

from dotfiles_manager.services.svg_template_cache_manager import (
    SVGTemplateCacheManager,
)


class WlogoutService:
    """Service for generating wlogout icons and styles."""

    def __init__(
        self,
        icons_templates_dir: Path,
        style_template_path: Path,
        svg_cache_manager: SVGTemplateCacheManager | None = None,
    ):
        """Initialize wlogout service.

        Args:
            icons_templates_dir: Directory containing SVG icon templates
            style_template_path: Path to style.css.tpl template
            svg_cache_manager: Optional SVG cache manager for caching rendered templates
        """
        self._icons_templates_dir = icons_templates_dir
        self._style_template_path = style_template_path
        self._svg_cache = svg_cache_manager

    def generate_icons(self, color: str, output_dir: Path) -> dict[str, Path]:
        """Generate wlogout icons from SVG templates.

        Uses SVG cache if available to avoid re-rendering templates with the same color.

        Args:
            color: Hex color to use (e.g., "#ffffff")
            output_dir: Directory to write generated icons

        Returns:
            Dict mapping icon name to output path
        """
        from dotfiles_template_renderer import Jinja2Renderer

        output_dir.mkdir(parents=True, exist_ok=True)

        icon_names = [
            "lock",
            "logout",
            "logout",
            "suspend",
            "hibernate",
            "shutdown",
            "reboot",
        ]

        generated_icons = {}

        # Compute colorscheme hash for cache key (use color as simple colorscheme)
        colorscheme = {"icon_color": color}
        colorscheme_hash = None
        if self._svg_cache:
            colorscheme_hash = self._svg_cache.compute_colorscheme_hash(
                colorscheme
            )

        # Create renderer for icon templates
        renderer = Jinja2Renderer(self._icons_templates_dir)

        for icon_name in icon_names:
            template_name = f"{icon_name}.svg"
            output_path = output_dir / template_name

            template_path = self._icons_templates_dir / template_name
            if not template_path.exists():
                continue

            # Try to get from cache first
            rendered = None
            if self._svg_cache and colorscheme_hash:
                rendered = self._svg_cache.get_cached_svg(
                    colorscheme_hash, template_name
                )

            # If not in cache, render template
            if rendered is None:
                context = {"CURRENT_COLOR": color}
                rendered = renderer.render(template_name, context)

                # Cache the rendered SVG
                if self._svg_cache and colorscheme_hash:
                    self._svg_cache.cache_svg(
                        colorscheme_hash, template_name, rendered
                    )

            # Write to file
            output_path.write_text(rendered)

            generated_icons[icon_name] = output_path

        return generated_icons

    def generate_style(
        self,
        font_family: str,
        font_size: int,
        colors_css_path: Path,
        background_image: Path,
        icons_dir: Path,
        output_path: Path,
    ) -> None:
        """Generate wlogout style.css from template.

        Args:
            font_family: System font family
            font_size: System font size in pixels
            colors_css_path: Path to colorscheme CSS file
            background_image: Path to wallpaper
            icons_dir: Path to generated icons directory
            output_path: Path to write style.css
        """
        from dotfiles_template_renderer import Jinja2Renderer

        output_path.parent.mkdir(parents=True, exist_ok=True)

        context = {
            "COLORS_FILE_PATH": str(colors_css_path),
            "SYSTEM_FONT_FAMILY": font_family,
            "FONT_SIZE_PX": font_size,
            "BACKGROUND_IMAGE": str(background_image),
            "ICONS_DIR": str(icons_dir),
        }

        # Create renderer for style template
        template_dir = self._style_template_path.parent
        renderer = Jinja2Renderer(template_dir)

        # Render template
        template_name = self._style_template_path.name
        rendered = renderer.render(template_name, context)

        # Write to file
        output_path.write_text(rendered)

    def generate_all(
        self,
        color: str,
        font_family: str,
        font_size: int,
        colors_css_path: Path,
        background_image: Path,
        icons_output_dir: Path,
        style_output_path: Path,
    ) -> dict[str, Path]:
        """Generate both icons and style.

        Args:
            color: Hex color for icons
            font_family: System font family
            font_size: System font size in pixels
            colors_css_path: Path to colorscheme CSS file
            background_image: Path to wallpaper
            icons_output_dir: Directory to write icons
            style_output_path: Path to write style.css

        Returns:
            Dict with generated file paths
        """
        # Generate icons
        icons = self.generate_icons(color, icons_output_dir)

        # Generate style
        self.generate_style(
            font_family=font_family,
            font_size=font_size,
            colors_css_path=colors_css_path,
            background_image=background_image,
            icons_dir=icons_output_dir,
            output_path=style_output_path,
        )

        return {
            "icons": icons,
            "style": style_output_path,
        }

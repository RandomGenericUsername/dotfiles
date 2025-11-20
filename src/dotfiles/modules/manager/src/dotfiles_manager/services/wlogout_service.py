"""Wlogout service for generating icons and styles."""

from pathlib import Path

from icon_generator import IconRegistry, IconService
from icon_generator.models.requests import IconGenerationRequest


class WlogoutService:
    """Service for generating wlogout icons and styles.

    This service uses the generic icon-generator module for icon generation
    and handles wlogout-specific style.css generation.
    """

    def __init__(
        self,
        icon_registry: IconRegistry,
        icon_service: IconService,
        style_template_path: Path,
        icons_output_dir: Path,
        color_key: str = "color15",
    ):
        """Initialize wlogout service.

        Args:
            icon_registry: Icon registry for discovering wlogout icons
            icon_service: Icon service for generating icons with caching
            style_template_path: Path to style.css.tpl template
            icons_output_dir: Directory to write generated icons
            color_key: Which color from colorscheme to use (default: color15)
        """
        self._icon_registry = icon_registry
        self._icon_service = icon_service
        self._style_template_path = style_template_path
        self._icons_output_dir = icons_output_dir
        self._color_key = color_key

    def generate_icons(
        self, colorscheme: dict[str, str], output_dir: Path
    ) -> dict[str, Path]:
        """Generate wlogout icons from SVG templates.

        Uses IconService with integrated caching.

        Args:
            colorscheme: Full colorscheme dict (all 16 colors + special colors)
            output_dir: Directory to write generated icons

        Returns:
            Dict mapping icon name to output path
        """
        # Extract the primary color for icon rendering
        color = colorscheme.get(self._color_key, "#ffffff")

        # Create icon generation request
        request = IconGenerationRequest(
            category="wlogout-icons",
            variant=None,  # Flat structure, no variants
            color=color,
            colorscheme_data=colorscheme,
            output_dir=output_dir,
        )

        # Generate icons
        result = self._icon_service.generate_icons(request)

        return result.generated_icons

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
        colorscheme: dict[str, str],
        font_family: str,
        font_size: int,
        colors_css_path: Path,
        background_image: Path,
        style_output_path: Path,
    ) -> dict[str, Path]:
        """Generate both icons and style.

        Args:
            colorscheme: Full colorscheme dict (all 16 colors + special colors)
            font_family: System font family
            font_size: System font size in pixels
            colors_css_path: Path to colorscheme CSS file
            background_image: Path to wallpaper
            style_output_path: Path to write style.css

        Returns:
            Dict with generated file paths
        """
        # Generate icons using IconService
        icons = self.generate_icons(colorscheme, self._icons_output_dir)

        # Generate style
        self.generate_style(
            font_family=font_family,
            font_size=font_size,
            colors_css_path=colors_css_path,
            background_image=background_image,
            icons_dir=self._icons_output_dir,
            output_path=style_output_path,
        )

        return {
            "icons": icons,
            "style": style_output_path,
        }

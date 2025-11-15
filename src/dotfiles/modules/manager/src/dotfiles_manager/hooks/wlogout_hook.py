"""Wlogout icons hook."""

import json
from pathlib import Path

from dotfiles_manager.hooks.base import Hook
from dotfiles_manager.models.hook import HookContext, HookResult
from dotfiles_manager.services.wlogout_service import WlogoutService


class WlogoutIconsHook(Hook):
    """Hook to generate wlogout icons after wallpaper change."""

    def __init__(
        self,
        wlogout_service: WlogoutService,
        icons_output_dir: Path,
        style_output_path: Path,
    ):
        """Initialize wlogout icons hook.

        Args:
            wlogout_service: Wlogout service instance
            icons_output_dir: Directory to write generated icons
            style_output_path: Path to write style.css
        """
        self._wlogout_service = wlogout_service
        self._icons_output_dir = icons_output_dir
        self._style_output_path = style_output_path

    @property
    def name(self) -> str:
        """Unique identifier for this hook."""
        return "wlogout_icons"

    def execute(self, context: HookContext) -> HookResult:
        """Execute hook to generate wlogout icons and style.

        Args:
            context: Hook execution context

        Returns:
            HookResult: Result of hook execution
        """
        try:
            # Get colorscheme color key from config
            color_key = context.config.get("colorscheme_color_key", "color15")

            # Extract color from colorscheme JSON
            colorscheme_json_path = context.colorscheme_files.get("json")
            if not colorscheme_json_path or not colorscheme_json_path.exists():
                return HookResult(
                    success=False,
                    message="Colorscheme JSON file not found",
                )

            color = self._extract_color(colorscheme_json_path, color_key)

            # Get GTK CSS colorscheme path for style template
            colorscheme_gtk_css_path = context.colorscheme_files.get("gtk.css")
            if (
                not colorscheme_gtk_css_path
                or not colorscheme_gtk_css_path.exists()
            ):
                return HookResult(
                    success=False,
                    message="Colorscheme GTK CSS file not found",
                )

            # Generate icons and style
            generated = self._wlogout_service.generate_all(
                color=color,
                font_family=context.font_family,
                font_size=context.font_size,
                colors_css_path=colorscheme_gtk_css_path,
                background_image=context.wallpaper_path,
                icons_output_dir=self._icons_output_dir,
                style_output_path=self._style_output_path,
            )

            return HookResult(
                success=True,
                message=f"Generated {len(generated['icons'])} icons and style.css",
                data=generated,
            )

        except Exception as e:
            return HookResult(
                success=False,
                message=f"Failed to generate wlogout icons: {e}",
            )

    def _extract_color(
        self, colorscheme_json_path: Path, color_key: str
    ) -> str:
        """Extract color from colorscheme JSON.

        Args:
            colorscheme_json_path: Path to colorscheme JSON file
            color_key: Color key to extract (e.g., "color15")

        Returns:
            Hex color string (e.g., "#ffffff")
        """
        data = json.loads(colorscheme_json_path.read_text())
        colors = data.get("colors", {})
        return colors.get(color_key, "#ffffff")

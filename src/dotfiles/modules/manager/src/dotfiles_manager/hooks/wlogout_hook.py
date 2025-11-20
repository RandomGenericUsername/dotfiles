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
        style_output_path: Path,
    ):
        """Initialize wlogout icons hook.

        Args:
            wlogout_service: Wlogout service instance
            style_output_path: Path to write style.css
        """
        self._wlogout_service = wlogout_service
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
            # Skip if colorscheme was not generated
            if not context.colorscheme_generated:
                return HookResult(
                    success=True,
                    message="Skipped (no colorscheme generated)",
                )

            # Extract full colorscheme from JSON
            colorscheme_json_path = context.colorscheme_files.get("json")
            if not colorscheme_json_path or not colorscheme_json_path.exists():
                return HookResult(
                    success=False,
                    message="Colorscheme JSON file not found",
                )

            colorscheme = self._load_colorscheme(colorscheme_json_path)

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
                colorscheme=colorscheme,
                font_family=context.font_family,
                font_size=context.font_size,
                colors_css_path=colorscheme_gtk_css_path,
                background_image=context.wallpaper_path,
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

    def _load_colorscheme(self, colorscheme_json_path: Path) -> dict[str, str]:
        """Load full colorscheme from JSON file.

        Args:
            colorscheme_json_path: Path to colorscheme JSON file

        Returns:
            Dict with all colors (color0-color15 + special colors)
        """
        data = json.loads(colorscheme_json_path.read_text())
        colors = data.get("colors", {})

        # Build colorscheme dict with all colors
        colorscheme = {}

        # Add standard colors (color0-color15)
        for i in range(16):
            key = f"color{i}"
            if key in colors:
                colorscheme[key] = colors[key]

        # Add special colors
        special_colors = [
            "background",
            "foreground",
            "cursor",
        ]
        for key in special_colors:
            if key in colors:
                colorscheme[key] = colors[key]

        return colorscheme

"""Render context model for rofi templates."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from rofi_config_manager.models.modi import ModiConfig


class RofiRenderContext(BaseModel):
    """Context for rendering rofi templates."""

    # System attributes
    font_family: str
    font_size: int
    border_width: int = Field(default=2, ge=0)

    # Colorscheme (inline, no file imports)
    background: str
    foreground: str
    cursor: str
    colors: List[str] = Field(
        default_factory=list, min_length=16, max_length=16
    )

    # Current wallpaper
    current_wallpaper: Optional[Path] = None

    # Modi configuration
    modi: ModiConfig = Field(default_factory=ModiConfig)

    # Configuration block settings
    sidebar_mode: bool = False
    click_to_exit: bool = False
    show_icons: bool = True
    scroll_method: int = 0

    def to_template_dict(self) -> Dict[str, Any]:
        """Convert to template variables dict.

        Returns:
            Dict suitable for Jinja2 template rendering
        """
        template_vars: Dict[str, Any] = {
            # System attributes
            "FONT_FAMILY": self.font_family,
            "FONT_SIZE": self.font_size,
            "BORDER_WIDTH": self.border_width,
            # Colors
            "BACKGROUND": self.background,
            "FOREGROUND": self.foreground,
            "CURSOR": self.cursor,
            "COLORS": self.colors,  # Pass as list for loop iteration
            # Wallpaper
            "CURRENT_WALLPAPER": (
                str(self.current_wallpaper) if self.current_wallpaper else ""
            ),
            # Modi
            "HAS_MODI": self.modi.has_modi,
            "MODI_STRING": self.modi.to_rofi_config_string(),
            # Configuration block
            "SIDEBAR_MODE": self.sidebar_mode,
            "CLICK_TO_EXIT": self.click_to_exit,
            "SHOW_ICONS": self.show_icons,
            "SCROLL_METHOD": self.scroll_method,
        }

        # Add individual color variables for direct access
        for i, color in enumerate(self.colors):
            template_vars[f"COLOR{i}"] = color

        return template_vars

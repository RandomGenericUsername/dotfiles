"""Config type definitions and schemas."""

from enum import Enum

from pydantic import BaseModel, Field

from rofi_config_manager.models.modi import ModiConfig, RofiModi


class ConfigSchema(BaseModel):
    """Schema defining the structure of a rofi config type."""

    # System requirements
    requires_font: bool = True
    requires_colors: bool = True
    requires_wallpaper: bool = True
    requires_border: bool = True

    # Modi configuration
    modi: ModiConfig = Field(default_factory=ModiConfig)

    # Additional styling
    sidebar_mode: bool = False
    click_to_exit: bool = False
    show_icons: bool = True
    scroll_method: int = 0


class RofiConfigType(str, Enum):
    """Rofi configuration types."""

    WALLPAPER_SELECTOR = "wallpaper-selector"
    COLORSCHEME_VIEWER = "colorscheme-viewer"
    COLORSCHEME_VIEWER_MINIMAL = "colorscheme-viewer-minimal"

    @property
    def template_name(self) -> str:
        """Get template filename for this config type.

        Returns:
            Template filename
        """
        return f"{self.value}.rasi.j2"

    @property
    def output_filename(self) -> str:
        """Get output filename for this config type.

        Returns:
            Output filename
        """
        return f"{self.value}.rasi"

    @property
    def schema(self) -> ConfigSchema:
        """Get schema for this config type.

        Returns:
            Config schema with default settings
        """
        schemas = {
            self.WALLPAPER_SELECTOR: ConfigSchema(
                requires_border=True,
                sidebar_mode=True,
                click_to_exit=False,
                modi=ModiConfig(
                    enabled=True,
                    modi_list=[
                        RofiModi(
                            name="wallpapers",
                            script="rofi-wallpaper-selector wallpapers",
                        ),
                        RofiModi(
                            name="effects",
                            script="rofi-wallpaper-selector effects",
                        ),
                    ],
                ),
            ),
            self.COLORSCHEME_VIEWER: ConfigSchema(
                requires_border=True,
                sidebar_mode=False,
                click_to_exit=False,
                modi=ModiConfig(enabled=False),  # No modi
            ),
            self.COLORSCHEME_VIEWER_MINIMAL: ConfigSchema(
                requires_border=False,
                sidebar_mode=False,
                click_to_exit=True,
                modi=ModiConfig(enabled=False),  # No modi
            ),
        }
        return schemas[self]

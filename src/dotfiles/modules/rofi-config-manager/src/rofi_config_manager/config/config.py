"""Application configuration."""

from pathlib import Path

from dynaconf import Dynaconf
from pydantic import BaseModel, Field

from rofi_config_manager.models.modi import ModiConfig, RofiModi


class PathsConfig(BaseModel):
    """Paths configuration."""

    dotfiles_manager_path: Path
    rofi_wallpaper_selector_cli: Path
    templates_dir: Path
    output_dir: Path


class StylingOverride(BaseModel):
    """Per-config styling overrides."""

    border_width: int | None = None


class StylingConfig(BaseModel):
    """Styling configuration."""

    default_border_width: int = Field(default=2, ge=0)
    overrides: dict[str, StylingOverride] = Field(default_factory=dict)

    def get_border_width(self, config_name: str) -> int:
        """Get border width for a specific config.

        Args:
            config_name: Config type name

        Returns:
            Border width in pixels
        """
        override = self.overrides.get(config_name)
        if override and override.border_width is not None:
            return override.border_width
        return self.default_border_width


class AppConfig(BaseModel):
    """Application configuration."""

    paths: PathsConfig
    configs: dict[str, bool]  # enabled configs
    styling: StylingConfig
    modi: dict[str, list[RofiModi]] = Field(
        default_factory=dict
    )  # Modi per config type

    def get_modi_config(self, config_name: str) -> ModiConfig:
        """Get modi configuration for a specific config type.

        Args:
            config_name: Config type name (e.g., "wallpaper-selector")

        Returns:
            ModiConfig with list of modi for this config
        """
        modi_list = self.modi.get(config_name, [])
        return ModiConfig(
            enabled=len(modi_list) > 0,
            modi_list=modi_list,
        )


def load_config(config_path: Path | None = None) -> AppConfig:
    """Load application configuration.

    Args:
        config_path: Optional path to config file

    Returns:
        Loaded application configuration
    """
    if config_path:
        settings = Dynaconf(
            settings_files=[str(config_path)],
            envvar_prefix="ROFI_CONFIG_MANAGER",
        )
    else:
        # Load from default location
        default_config = (
            Path(__file__).parent.parent.parent.parent
            / "config"
            / "settings.toml"
        )
        settings = Dynaconf(
            settings_files=[str(default_config)],
            envvar_prefix="ROFI_CONFIG_MANAGER",
        )

    # Get rofi-wallpaper-selector CLI path for substitution
    rofi_wallpaper_selector_cli = Path(
        settings.paths.rofi_wallpaper_selector_cli
    ).expanduser()

    # Parse modi configuration with path substitution
    modi_dict: dict[str, list[RofiModi]] = {}
    if hasattr(settings, "modi"):
        for config_name, modi_list in settings.modi.items():
            modi_dict[config_name] = [
                RofiModi(
                    name=m["name"],
                    script=m["script"].format(
                        rofi_wallpaper_selector_cli=str(
                            rofi_wallpaper_selector_cli
                        )
                    ),
                )
                for m in modi_list
            ]

    # Parse enabled configs
    enabled_configs: dict[str, bool] = {}
    if hasattr(settings, "configs") and hasattr(settings.configs, "enabled"):
        for config_name in settings.configs.enabled:
            enabled_configs[config_name] = True

    # Parse styling overrides
    overrides: dict[str, StylingOverride] = {}
    if hasattr(settings, "styling") and hasattr(settings.styling, "overrides"):
        for config_name, override_data in settings.styling.overrides.items():
            border_width = (
                override_data.get("border_width")
                if isinstance(override_data, dict)
                else None
            )
            overrides[config_name] = StylingOverride(border_width=border_width)

    # Resolve templates_dir relative to module root if it's relative
    templates_dir = Path(settings.paths.templates_dir)
    if not templates_dir.is_absolute():
        # Resolve relative to src/rofi_config_manager/
        module_root = Path(__file__).parent.parent
        templates_dir = module_root / templates_dir
    else:
        templates_dir = templates_dir.expanduser()

    return AppConfig(
        paths=PathsConfig(
            dotfiles_manager_path=Path(
                settings.paths.dotfiles_manager_path
            ).expanduser(),
            rofi_wallpaper_selector_cli=rofi_wallpaper_selector_cli,
            templates_dir=templates_dir,
            output_dir=Path(settings.paths.output_dir).expanduser(),
        ),
        configs=enabled_configs,
        styling=StylingConfig(
            default_border_width=settings.styling.default_border_width,
            overrides=overrides,
        ),
        modi=modi_dict,
    )

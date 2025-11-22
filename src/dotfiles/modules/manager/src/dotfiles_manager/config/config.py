"""Configuration models for dotfiles manager."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class ManagerConfig(BaseModel):
    """Configuration for the Manager.

    Attributes:
        state_db_path: Path to the state database.
        debug: Enable debug mode.
        icon_variant: Default icon variant for all categories.
        icon_variant_overrides: Per-category icon variant overrides.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )

    state_db_path: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / "state"
        / "manager"
        / "system.db",
        description="Path to the state database",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    icon_variant: str = Field(
        default="solid",
        description="Default icon variant for all categories",
    )
    icon_variant_overrides: dict[str, str] = Field(
        default_factory=dict,
        description="Per-category icon variant overrides",
    )


class SystemConfig(BaseModel):
    """System attributes configuration.

    Attributes:
        font_family: System font family.
        font_size: System font size in pixels.
        monitors: List of monitor names.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )

    font_family: str = Field(
        default="JetBrains Mono",
        description="System font family",
    )
    font_size: int = Field(
        default=14,
        description="System font size in pixels",
    )
    monitors: list[str] = Field(
        default_factory=list,
        description="List of monitor names (empty = auto-detect)",
    )


class PathsConfig(BaseModel):
    """Paths configuration.

    Attributes:
        install_root: Installation root directory.
        wallpaper_orchestrator_path: Path to wallpaper orchestrator.
        colorscheme_orchestrator_path: Path to colorscheme orchestrator.
        rofi_config_manager_cli: Path to rofi-config-manager CLI.
        status_bar_icons_base_dir: Base directory for status bar icon templates.
        status_bar_icons_output_dir: Directory for generated status bar icons.
        wlogout_icons_templates_dir: Directory for wlogout icon templates.
        wlogout_style_template_path: Path to wlogout style template.
        wlogout_icons_output_dir: Directory for generated wlogout icons.
        wlogout_style_output_path: Path to generated wlogout style.
        wlogout_config_dir: Directory for wlogout config.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )

    install_root: Path = Field(
        default=Path.home() / ".local" / "share" / "dotfiles",
        description="Installation root directory",
    )
    wallpaper_orchestrator_path: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / ".dependencies"
        / "tools"
        / "wallpaper-orchestrator",
        description="Path to wallpaper orchestrator",
    )
    colorscheme_orchestrator_path: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / ".dependencies"
        / "tools"
        / "colorscheme-orchestrator",
        description="Path to colorscheme orchestrator",
    )
    rofi_config_manager_cli: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / ".dependencies"
        / "modules"
        / "rofi-config-manager"
        / ".venv"
        / "bin"
        / "rofi-config-manager",
        description="Path to rofi-config-manager CLI",
    )
    status_bar_icons_base_dir: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / "dotfiles"
        / "assets"
        / "status-bar-icons",
        description="Base directory for status bar icon templates",
    )
    status_bar_icons_output_dir: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / "dotfiles"
        / "eww"
        / "status-bar"
        / "icons",
        description="Directory for generated status bar icons",
    )
    wlogout_icons_templates_dir: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / "dotfiles"
        / "assets"
        / "wlogout-icons",
        description="Directory for wlogout icon templates",
    )
    wlogout_style_template_path: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / "dotfiles"
        / "wlogout"
        / "templates"
        / "style.css.tpl",
        description="Path to wlogout style template",
    )
    wlogout_icons_output_dir: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / "dotfiles"
        / "wlogout"
        / "icons",
        description="Directory for generated wlogout icons",
    )
    wlogout_style_output_path: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / "dotfiles"
        / "wlogout"
        / "style.css",
        description="Path to generated wlogout style",
    )
    wlogout_config_dir: Path = Field(
        default=Path.home()
        / ".local"
        / "share"
        / "dotfiles"
        / "dotfiles"
        / "config"
        / "wlogout",
        description="Directory for wlogout config",
    )


class HooksConfig(BaseModel):
    """Hooks configuration.

    Attributes:
        enabled: List of enabled hook names.
        fail_fast: Stop execution if a critical hook fails.
        execution_groups: List of execution groups with hooks and mode.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",  # Allow extra fields for individual hook configs
    )

    enabled: list[str] = Field(
        default_factory=lambda: ["wlogout_icons"],
        description="List of enabled hook names",
    )
    fail_fast: bool = Field(
        default=False,
        description="Stop execution if a critical hook fails",
    )
    execution_groups: list[dict] = Field(
        default_factory=list,
        description="List of execution groups with hooks and mode",
    )

    def model_dump(self, **kwargs) -> dict:
        """Convert to dict including extra fields."""
        # Get base dict
        data = super().model_dump(**kwargs)
        # Add any extra fields that were set
        for key, value in self.__dict__.items():
            if key not in data and not key.startswith("_"):
                data[key] = value
        return data


class SVGCacheConfig(BaseModel):
    """Configuration for SVG template cache.

    Controls SVG rendering cache behavior and limits.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )

    enabled: bool = Field(
        default=True,
        description="Enable SVG template caching",
    )
    max_cache_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum cache size in MB",
    )
    enable_lru: bool = Field(
        default=True,
        description="Enable LRU eviction when cache is full",
    )
    preload_on_startup: bool = Field(
        default=False,
        description="Preload cache on startup (not recommended)",
    )


class AppConfig(BaseModel):
    """Application-level configuration.

    Attributes:
        manager: Manager-specific configuration.
        system: System attributes configuration.
        paths: Paths configuration.
        hooks: Hooks configuration.
        svg_cache: SVG template cache configuration.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )

    manager: ManagerConfig = Field(
        default_factory=ManagerConfig,
        description="Manager configuration",
    )
    system: SystemConfig = Field(
        default_factory=SystemConfig,
        description="System attributes configuration",
    )
    paths: PathsConfig = Field(
        default_factory=PathsConfig,
        description="Paths configuration",
    )
    hooks: HooksConfig = Field(
        default_factory=HooksConfig,
        description="Hooks configuration",
    )
    svg_cache: SVGCacheConfig = Field(
        default_factory=SVGCacheConfig,
        description="SVG template cache configuration",
    )

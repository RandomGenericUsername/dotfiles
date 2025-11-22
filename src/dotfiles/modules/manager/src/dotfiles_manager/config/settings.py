"""Settings loader for dotfiles manager."""

from pathlib import Path

from dynaconf import Dynaconf

from dotfiles_manager.config.config import (
    AppConfig,
    HooksConfig,
    ManagerConfig,
    PathsConfig,
    SystemConfig,
)


def get_settings() -> Dynaconf:
    """Load settings from configuration files.

    Loads settings from:
    1. Module's config/settings.toml (defaults)
    2. ~/.config/dotfiles-manager/settings.toml (user overrides)

    Returns:
        Dynaconf settings object.
    """
    # Get the module's config directory
    module_dir = Path(__file__).parent.parent.parent.parent
    config_dir = module_dir / "config"

    settings = Dynaconf(
        envvar_prefix="DOTFILES_MANAGER",
        settings_files=[
            str(config_dir / "settings.toml"),
            str(
                Path.home() / ".config" / "dotfiles-manager" / "settings.toml"
            ),
        ],
        merge_enabled=True,
    )

    return settings


def load_config() -> AppConfig:
    """Load full application configuration from settings files.

    Returns:
        AppConfig loaded from configuration files.
    """
    settings = get_settings()

    # Load manager config
    manager_config = ManagerConfig(
        state_db_path=Path(settings.get("manager.state_db_path")).expanduser(),
        debug=settings.get("manager.debug", False),
        icon_variant=settings.get("manager.icon_variant", "solid"),
        icon_variant_overrides=settings.get(
            "manager.icon_variant_overrides", {}
        ),
    )

    # Load system config
    system_config = SystemConfig(
        font_family=settings.get("system.font_family", "JetBrains Mono"),
        font_size=settings.get("system.font_size", 14),
        monitors=settings.get("system.monitors", []),
    )

    # Load paths config
    # First get install_root to use for template substitution
    install_root = Path(settings.get("paths.install_root")).expanduser()

    # Helper function to resolve path templates
    def resolve_path(path_str: str) -> Path:
        """Resolve path template with {install_root} substitution."""
        resolved = path_str.replace("{install_root}", str(install_root))
        return Path(resolved).expanduser()

    paths_config = PathsConfig(
        install_root=install_root,
        wallpaper_orchestrator_path=resolve_path(
            settings.get("paths.wallpaper_orchestrator_path")
        ),
        colorscheme_orchestrator_path=resolve_path(
            settings.get("paths.colorscheme_orchestrator_path")
        ),
        rofi_config_manager_cli=resolve_path(
            settings.get("paths.rofi_config_manager_cli")
        ),
        status_bar_icons_base_dir=resolve_path(
            settings.get("paths.status_bar_icons_base_dir")
        ),
        status_bar_icons_output_dir=resolve_path(
            settings.get("paths.status_bar_icons_output_dir")
        ),
        wlogout_icons_templates_dir=resolve_path(
            settings.get("paths.wlogout_icons_templates_dir")
        ),
        wlogout_style_template_path=resolve_path(
            settings.get("paths.wlogout_style_template_path")
        ),
        wlogout_icons_output_dir=resolve_path(
            settings.get("paths.wlogout_icons_output_dir")
        ),
        wlogout_style_output_path=resolve_path(
            settings.get("paths.wlogout_style_output_path")
        ),
        wlogout_config_dir=resolve_path(
            settings.get("paths.wlogout_config_dir")
        ),
    )

    # Load hooks config - get all hooks settings as dict
    hooks_dict = settings.get("hooks", {})

    # Create HooksConfig with all fields
    hooks_config = HooksConfig(
        enabled=hooks_dict.get("enabled", ["wlogout_icons"]),
        fail_fast=hooks_dict.get("fail_fast", False),
        execution_groups=hooks_dict.get("execution_groups", []),
    )

    # Add individual hook configs as extra fields
    for key, value in hooks_dict.items():
        if key not in ["enabled", "fail_fast", "execution_groups"]:
            setattr(hooks_config, key, value)

    return AppConfig(
        manager=manager_config,
        system=system_config,
        paths=paths_config,
        hooks=hooks_config,
    )


def get_default_config() -> AppConfig:
    """Get default application configuration.

    Returns:
        AppConfig with default values.
    """
    return AppConfig()


def get_manager_config() -> ManagerConfig:
    """Get manager configuration from settings files.

    Returns:
        ManagerConfig loaded from configuration files.
    """
    settings = get_settings()

    # Extract manager configuration
    manager_config = ManagerConfig(
        state_db_path=Path(
            settings.get(
                "manager.state_db_path", ManagerConfig().state_db_path
            )
        ),
        debug=settings.get("manager.debug", False),
    )

    return manager_config

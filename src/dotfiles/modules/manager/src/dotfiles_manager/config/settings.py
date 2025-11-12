"""Settings loader for dotfiles manager."""

from pathlib import Path

from dynaconf import Dynaconf

from dotfiles_manager.config.config import AppConfig, ManagerConfig


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
        data_dir=Path(
            settings.get("manager.data_dir", ManagerConfig().data_dir)
        ),
        debug=settings.get("manager.debug", False),
    )

    return manager_config

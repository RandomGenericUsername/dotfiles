"""Settings loader using dynaconf."""

from pathlib import Path

from dynaconf import Dynaconf

from dotfiles_state_manager.config.config import AppConfig, StateManagerConfig


def _get_settings_files() -> list[str]:
    """Get list of settings files to load.
    
    Priority (highest to lowest):
    1. User config: ~/.config/state-manager/settings.toml
    2. Local config: ./config/settings.toml
    """
    files = []
    
    # Local config (in module directory)
    local_config = Path(__file__).parent.parent.parent.parent / "config" / "settings.toml"
    if local_config.exists():
        files.append(str(local_config))
    
    # User config
    user_config = Path.home() / ".config/state-manager/settings.toml"
    if user_config.exists():
        files.append(str(user_config))
    
    return files


def get_default_config() -> AppConfig:
    """Get default configuration.
    
    Returns:
        AppConfig with default values
    """
    settings_files = _get_settings_files()
    
    if settings_files:
        # Load from files
        dynaconf_settings = Dynaconf(
            settings_files=settings_files,
            merge_enabled=True,
        )
        config_dict = dynaconf_settings.to_dict()
    else:
        # Use defaults
        config_dict = {}
    
    return AppConfig(**config_dict)


def get_state_manager_config() -> StateManagerConfig:
    """Get state manager configuration.
    
    Returns:
        StateManagerConfig with values from settings files or defaults
    """
    app_config = get_default_config()
    return app_config.state_manager


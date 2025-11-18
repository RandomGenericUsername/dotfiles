"""Settings loader using dynaconf."""

from pathlib import Path

from dynaconf import Dynaconf  # type: ignore[import-untyped]

from dotfiles_socket.config.config import (
    AppConfig,
    SocketConfig,
    SocketModuleConfig,
    TcpSocketConfig,
    UnixSocketConfig,
)


def _get_settings_files() -> list[str]:
    """Get list of settings files to load.

    Priority (highest to lowest):
    1. User config: ~/.config/socket/settings.toml
    2. Local config: ./config/settings.toml

    Returns:
        List of settings file paths
    """
    files = []

    # Local config (in module directory)
    local_config = (
        Path(__file__).parent.parent.parent.parent / "config" / "settings.toml"
    )
    if local_config.exists():
        files.append(str(local_config))

    # User config
    user_config = Path.home() / ".config/socket/settings.toml"
    if user_config.exists():
        files.append(str(user_config))

    return files


def get_default_config() -> AppConfig:
    """Get default configuration.

    Loads configuration from settings files if available,
    otherwise uses default values.

    Returns:
        AppConfig with values from settings files or defaults
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


def get_socket_config() -> SocketModuleConfig:
    """Get socket module configuration.

    Returns:
        SocketModuleConfig with values from settings files or defaults
    """
    app_config = get_default_config()
    return app_config.socket


def get_generic_socket_config() -> SocketConfig:
    """Get generic socket configuration.

    Returns:
        SocketConfig with values from settings files or defaults
    """
    socket_config = get_socket_config()
    return socket_config.socket


def get_unix_socket_config() -> UnixSocketConfig:
    """Get Unix socket configuration.

    Returns:
        UnixSocketConfig with values from settings files or defaults
    """
    socket_config = get_socket_config()
    return socket_config.unix


def get_tcp_socket_config() -> TcpSocketConfig:
    """Get TCP socket configuration.

    Returns:
        TcpSocketConfig with values from settings files or defaults
    """
    socket_config = get_socket_config()
    return socket_config.tcp

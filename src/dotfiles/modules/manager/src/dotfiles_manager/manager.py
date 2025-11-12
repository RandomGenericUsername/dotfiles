"""Main Manager implementation."""

from typing import Any

from dotfiles_logging import Log, LogLevels

from dotfiles_manager.config import ManagerConfig, get_manager_config


class Manager:
    """Generic manager for dotfiles components.

    Provides a flexible framework for managing dotfiles components,
    configurations, and resources.

    Args:
        config: Optional ManagerConfig instance. If not provided,
                loads from default configuration files.

    Example:
        >>> manager = Manager()
        >>> # Use manager functionality
    """

    def __init__(self, config: ManagerConfig | None = None) -> None:
        """Initialize the Manager.

        Args:
            config: Optional configuration. If None, loads default config.
        """
        self.config = config or get_manager_config()
        log_level = LogLevels.DEBUG if self.config.debug else LogLevels.INFO
        self.logger = Log.create_logger(__name__, log_level=log_level)
        self.logger.debug("Manager initialized")

    def __enter__(self) -> "Manager":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Clean up resources."""
        self.logger.debug("Manager closed")

"""Configuration management for dotfiles manager."""

from dotfiles_manager.config.config import AppConfig, ManagerConfig
from dotfiles_manager.config.settings import (
    get_default_config,
    get_manager_config,
)

__all__ = [
    "AppConfig",
    "ManagerConfig",
    "get_default_config",
    "get_manager_config",
]

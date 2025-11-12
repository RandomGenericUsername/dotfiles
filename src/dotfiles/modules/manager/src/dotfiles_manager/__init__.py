"""Dotfiles Manager - Generic manager module for dotfiles components.

Provides a flexible framework for managing dotfiles components, configurations,
and resources.

Usage:
    from dotfiles_manager import Manager

    # Create manager instance
    manager = Manager()

    # Use manager functionality
    # (Implementation details to be added based on specific requirements)
"""

# Configuration
from dotfiles_manager.config import (
    AppConfig,
    ManagerConfig,
    get_default_config,
    get_manager_config,
)

# Main interface
from dotfiles_manager.manager import Manager

__all__ = [
    # Main interface
    "Manager",
    # Configuration
    "AppConfig",
    "ManagerConfig",
    "get_default_config",
    "get_manager_config",
]

__version__ = "0.1.0"

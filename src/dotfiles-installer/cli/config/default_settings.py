"""Default configuration values for the dotfiles installer.

This module contains ALL default values as Python objects.
User overrides should go in settings.toml files.

Configuration Hierarchy:
1. This file (default_settings.py) - Python defaults (LOWEST PRIORITY)
2. settings.toml (in cli/config) - Project settings
3. settings.toml (in project root) - User overrides (HIGHEST PRIORITY)
4. CLI arguments - Runtime overrides (HIGHEST PRIORITY)
"""

from pathlib import Path
from typing import Any

# ============================================================================
# User CLI Settings Defaults
# ============================================================================

CLI_SETTINGS_DEFAULTS: dict[str, Any] = {
    "installation_directory": Path.home() / "dotfiles",
    "backup_directory": Path.home() / "backup",
    "install_type": "update",  # Options: "update" or "clean"
    "hidden": True,  # Prefix install directory with dot
    "debug": {
        "log_level": "error",  # Options: "debug", "info", "warning", "error"
        "output_to_file": False,  # Write logs to file
        "log_directory": Path.home() / "logs",  # Path to log directory
    },
}


# ============================================================================
# Project Path Defaults
# ============================================================================
# NOTE: Path defaults have been moved to cli/config/directories.py
# This provides a scalable flat structure for managing 300+ directory paths.
# Paths are now accessed via SimpleNamespace objects:
#   - directories.source (project source files)
#   - directories.install (installation target paths)
#   - directories.host (user system directories)
#   - directories.runtime (logs, cache, etc.)

# ============================================================================
# Project Package Manager Defaults
# ============================================================================

PACKAGE_MANAGER_DEFAULTS: dict[str, bool] = {
    "prefer_third_party": True,  # Prefer paru/yay on Arch for AUR
    "update_system": True,  # Update system packages before installing
    "remove_dependencies": True,  # Remove unused dependencies
    "dry_run": False,  # Only check for updates (dry run mode)
}

# ============================================================================
# Project Container Manager Defaults
# ============================================================================

CONTAINER_MANAGER_DEFAULTS: dict[str, str | int | bool] = {
    "runtime": "docker",  # Options: "docker" or "podman"
    "build_timeout": 600,  # Build timeout in seconds
    "default_registry": "docker.io",
    "cache_enabled": True,
}

# ============================================================================
# Project Template Renderer Defaults
# ============================================================================

TEMPLATE_RENDERER_DEFAULTS: dict[str, bool] = {
    "strict_mode": True,  # Fail on missing template variables
}

# ============================================================================
# Project Safety Defaults
# ============================================================================

PROTECTED_DIRECTORIES = [
    # System root and core directories
    "/",
    "/root",
    "/usr",
    "/etc",
    "/var",
    "/bin",
    "/sbin",
    "/lib",
    "/boot",
    "/sys",
    "/proc",
    "/dev",
    # User and home directories
    "/home",
    "/Users",
    # Mount points and external storage
    "/mnt",
    "/media",
    "/run/media",
    # Package managers and applications
    "/opt",
    "/usr/local",
    "/snap",
    "/opt/homebrew",
    "/flatpak",
    # Service and application data
    "/var/www",
    "/srv",
    "/var/lib",
    "/var/log",
    "/var/spool",
    # Common backup and temp locations
    "/backup",
    "/backups",
    "/tmp",
    "/var/tmp",
]

DIRECTORY_DELETION_DEFAULTS: dict[str, list[str] | int | bool] = {
    "protected_directories": PROTECTED_DIRECTORIES,
    "dangerous_keywords": ["system", "root", "backup", "config"],
    "minimum_path_depth": 3,
    "protect_user_homes": True,
    "keyword_check_depth_threshold": 4,
}

# ============================================================================
# Project System Defaults
# ============================================================================

SYSTEM_PACKAGES_DEFAULTS: dict[str, dict[str, Any]] = {
    "features": {},  # Feature versions (empty means not installed by default)
    # Examples:
    # "python": {"version": "3.12.0"},
    # "nodejs": {"version": "20.9.0"},
}

# NOTE: System packages, package configs, and features are loaded from
# distribution-specific files in config/packages/{distro}/system.toml
# based on the detected package manager (arch, debian, redhat)

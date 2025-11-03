import os
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf
from pydantic import ValidationError
from src.config.config import AppConfig as PydanticAppConfig
from src.config.enums import InstallType
from src.config.project_root import get_project_path


def _get_settings_files() -> list[str]:
    """Get configuration files in loading order.

    This function is called lazily to ensure project root is set before
    accessing configuration files.

    Configuration hierarchy (lowest to highest priority):
    1. Python defaults (config/default_settings.py) - Pydantic Field defaults
    2. settings.toml (cli/config) - Project settings
    3. system.toml (cli/config/packages/{distro}/) - Distro-specific packages
    4. settings.toml (root) - User overrides
    5. CLI arguments - Runtime overrides (handled in update() method)

    Returns:
        List of configuration file paths in loading order
    """
    # Configuration files (in loading order - later files override earlier)
    PROJECT_SETTINGS = get_project_path(
        "src/dotfiles-installer/cli/config/settings.toml"
    )
    SETTINGS_FILE = get_project_path("settings.toml")

    # Get distro-specific packages config
    from config.directories import get_distro_packages_path

    try:
        DISTRO_PACKAGES = get_distro_packages_path()
    except FileNotFoundError:
        # If distro config not found, skip it
        DISTRO_PACKAGES = None

    # Order matters! Later files override earlier ones.
    # Python defaults are in Pydantic Field defaults, not loaded from TOML
    files = [
        str(PROJECT_SETTINGS),  # 1. Project-level settings
    ]

    if DISTRO_PACKAGES:
        files.append(str(DISTRO_PACKAGES))  # 2. Distro-specific packages

    files.append(str(SETTINGS_FILE))  # 3. User overrides (highest priority)

    return files


class SettingsModel:
    def __init__(self, settings_files: list[str] | None = None):
        """Initialize settings model.

        Args:
            settings_files: List of configuration files to load.
                If None, will call _get_settings_files() to get them.
        """
        if settings_files is None:
            settings_files = _get_settings_files()

        self.dynaconf_settings: Dynaconf = Dynaconf(
            settings_files=settings_files,
            merge_enabled=True,  # Enable deep merging of nested dicts
        )
        self.settings: PydanticAppConfig = self.get_pydantic_config(
            self._convert_dict_to_lower_case(
                self._resolve_environment_variables(
                    self.dynaconf_settings.to_dict()
                )
            )
        )

    @staticmethod
    def _convert_dict_to_lower_case(
        settings_dict: dict[str, Any],
    ) -> dict[str, Any]:
        lower_case_dict = {}
        for key, value in settings_dict.items():
            if isinstance(value, dict):
                lower_case_dict[key.lower()] = (
                    SettingsModel._convert_dict_to_lower_case(value)
                )
            else:
                lower_case_dict[key.lower()] = value
        return lower_case_dict

    @staticmethod
    def _resolve_environment_variables(
        settings_dict: dict[str, Any],
    ) -> dict[str, Any]:
        def _resolve_string_values(data: Any) -> Any:
            """Recursively resolve env variables in nested structures."""
            if isinstance(data, str):
                return os.path.expandvars(data)
            elif isinstance(data, dict):
                return {
                    key: _resolve_string_values(value)
                    for key, value in data.items()
                }
            elif isinstance(data, list):
                return [_resolve_string_values(item) for item in data]
            else:
                return data

        return _resolve_string_values(settings_dict)

    @staticmethod
    def get_pydantic_config(settings: dict) -> PydanticAppConfig:
        try:
            return PydanticAppConfig(**settings)
        except ValidationError as e:
            raise e

    def get(self) -> PydanticAppConfig:
        return self.settings

    def update(
        self,
        log_level_str: str | None = None,
        install_directory: Path | None = None,
        backup_directory: Path | None = None,
        install_type: InstallType | None = None,
        hide: bool | None = None,
        log_to_file: bool | None = None,
        log_directory: Path | None = None,
    ) -> PydanticAppConfig:
        debug_updates = {}
        if log_level_str is not None:
            debug_updates["log_level"] = log_level_str
        if log_to_file is not None:
            debug_updates["output_to_file"] = log_to_file
        if log_directory is not None:
            debug_updates["log_directory"] = log_directory

        # Build update dictionary for CLI settings
        cli_settings_updates = {}
        if install_directory is not None:
            cli_settings_updates["installation_directory"] = install_directory
        if backup_directory is not None:
            cli_settings_updates["backup_directory"] = backup_directory
        if install_type is not None:
            cli_settings_updates["install_type"] = install_type
        if hide is not None:
            cli_settings_updates["hidden"] = hide

        if debug_updates:
            cli_settings_updates["debug"] = (
                self.settings.cli_settings.debug.model_copy(
                    update=debug_updates
                )
            )

        main_updates = {}
        if cli_settings_updates:
            main_updates["cli_settings"] = (
                self.settings.cli_settings.model_copy(
                    update=cli_settings_updates
                )
            )

        # Create updated settings
        updated = self.settings.model_copy(update=main_updates)

        return updated


# Global Settings singleton
# Initialized lazily when first accessed (after project root is set in main.py)
_settings_instance: SettingsModel | None = None


def _get_settings_instance() -> SettingsModel:
    """Get or create the global Settings instance.

    This ensures Settings is only initialized after project root is set.
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsModel()
    return _settings_instance


class _SettingsProxy:
    """Proxy object that lazily initializes Settings on first access."""

    def get(self) -> PydanticAppConfig:
        """Get the current configuration."""
        return _get_settings_instance().get()

    def update(
        self,
        log_level_str: str | None = None,
        install_directory: Path | None = None,
        backup_directory: Path | None = None,
        install_type: InstallType | None = None,
        hide: bool | None = None,
        log_to_file: bool | None = None,
        log_directory: Path | None = None,
    ) -> PydanticAppConfig:
        """Update settings with CLI arguments."""
        return _get_settings_instance().update(
            log_level_str=log_level_str,
            install_directory=install_directory,
            backup_directory=backup_directory,
            install_type=install_type,
            hide=hide,
            log_to_file=log_to_file,
            log_directory=log_directory,
        )


# Global Settings proxy - safe to import at module level
Settings = _SettingsProxy()


class _ProjectSettingsPath:
    """Lazy wrapper for PROJECT_SETTINGS path.

    This allows importing PROJECT_SETTINGS at module level without
    calling get_project_path() before project root is set.
    """

    _path: Path | None = None

    @property
    def parent(self) -> Path:
        """Get the parent directory of the project settings file."""
        if self._path is None:
            self._path = get_project_path(
                "src/dotfiles-installer/cli/config/settings.toml"
            )
        return self._path.parent

    def __truediv__(self, other: str) -> Path:
        """Allow path concatenation: PROJECT_SETTINGS / "file"."""
        if self._path is None:
            self._path = get_project_path(
                "src/dotfiles-installer/cli/config/settings.toml"
            )
        return self._path / other

    def __str__(self) -> str:
        """String representation."""
        if self._path is None:
            self._path = get_project_path(
                "src/dotfiles-installer/cli/config/settings.toml"
            )
        return str(self._path)


# Lazy constant for PROJECT_SETTINGS path
# Used by install.py to locate packages directory
PROJECT_SETTINGS = _ProjectSettingsPath()

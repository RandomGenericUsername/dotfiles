"""Settings override system for component installation.

Provides robust TOML modification with validation, backup, and rollback.
"""

import shutil
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli_w
from dotfiles_logging.rich.rich_logger import RichLogger
from pydantic import BaseModel, ValidationError

# ============================================================================
# Exceptions
# ============================================================================


class SettingsOverrideError(Exception):
    """Base exception for settings override operations."""

    pass


class ValidationFailedError(SettingsOverrideError):
    """Raised when settings validation fails."""

    pass


class TOMLOperationError(SettingsOverrideError):
    """Raised when TOML read/write operations fail."""

    pass


# ============================================================================
# Result Types
# ============================================================================


@dataclass
class OverrideResult:
    """Result of a settings override operation."""

    success: bool
    settings_file: Path
    overrides_applied: dict[str, Any]
    backup_file: Path | None = None
    errors: list[str] = field(default_factory=list)


# ============================================================================
# Settings Overrider
# ============================================================================


class SettingsOverrider:
    """Handles TOML settings file modifications with validation and rollback.

    This class provides a safe way to modify TOML configuration files with:
    - Automatic backup creation
    - Pydantic model validation
    - Rollback on failure
    - Deep merging of nested dictionaries
    - Comprehensive error handling

    Example:
        >>> overrider = SettingsOverrider(logger)
        >>> result = overrider.apply_overrides(
        ...     settings_file=Path("config/settings.toml"),
        ...     overrides={
        ...         "hyprpaper.wallpaper_dirs": ["~/wallpapers"],
        ...         "hyprpaper.max_preload_pool_mb": 200,
        ...     },
        ...     config_model=AppConfig,
        ... )
        >>> if result.success:
        ...     print(f"Applied {len(result.overrides_applied)} overrides")
    """

    def __init__(self, logger: RichLogger):
        """Initialize settings overrider.

        Args:
            logger: Logger instance for operation tracking
        """
        self.logger = logger

    def apply_overrides(
        self,
        settings_file: Path,
        overrides: dict[str, Any],
        config_model: type[BaseModel] | None = None,
    ) -> OverrideResult:
        """Apply overrides to a TOML settings file.

        This method:
        1. Creates a backup of the original file
        2. Loads the existing settings
        3. Applies overrides using dot notation (e.g., "section.key")
        4. Validates the result against a Pydantic model (if provided)
        5. Writes the modified settings back to the file
        6. Rolls back to backup if any step fails

        Args:
            settings_file: Path to settings.toml file
            overrides: Dictionary of overrides with dot notation keys
                      Example: {
                          "hyprpaper.wallpaper_dirs": ["~/custom"],
                          "hyprpaper.max_preload_pool_mb": 200,
                      }
            config_model: Optional Pydantic model for validation

        Returns:
            OverrideResult with operation details
        """
        result = OverrideResult(
            success=False,
            settings_file=settings_file,
            overrides_applied={},
        )

        try:
            # 1. Validate settings file exists
            if not settings_file.exists():
                raise TOMLOperationError(
                    f"Settings file not found: {settings_file}"
                )

            # 2. Create backup
            result.backup_file = self._create_backup(settings_file)
            self.logger.debug(f"Created backup: {result.backup_file}")

            # 3. Load existing settings
            settings = self._load_toml(settings_file)

            # 4. Apply each override
            for key, value in overrides.items():
                try:
                    self._apply_single_override(settings, key, value)
                    result.overrides_applied[key] = value
                    self.logger.debug(f"Applied override: {key} = {value}")
                except Exception as e:
                    error_msg = f"Failed to apply override '{key}': {e}"
                    result.errors.append(error_msg)
                    self.logger.warning(error_msg)

            # 5. Validate final settings if model provided
            if config_model:
                try:
                    self._validate_settings(settings, config_model)
                    self.logger.debug("Settings validation passed")
                except ValidationError as e:
                    raise ValidationFailedError(
                        f"Settings validation failed after applying overrides:\n{e}"
                    )

            # 6. Write modified settings
            self._write_toml(settings_file, settings)
            self.logger.info(
                f"Applied {len(result.overrides_applied)} overrides to "
                f"{settings_file.name}"
            )

            result.success = True
            return result

        except Exception as e:
            error_msg = f"Settings override failed: {e}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)

            # Rollback if backup exists
            if result.backup_file and result.backup_file.exists():
                try:
                    self._rollback(settings_file, result.backup_file)
                    self.logger.info("Rolled back to backup")
                except Exception as rollback_error:
                    self.logger.error(f"Rollback failed: {rollback_error}")

            return result

    def _apply_single_override(
        self,
        settings: dict,
        key: str,
        value: Any,
    ) -> None:
        """Apply a single override using dot notation.

        Supports nested keys like "hyprpaper.wallpaper_dirs".
        Uses deep merge for dictionaries to preserve existing keys.

        Args:
            settings: Settings dictionary to modify (modified in-place)
            key: Key in dot notation (e.g., "hyprpaper.wallpaper_dirs")
            value: Value to set

        Example:
            >>> settings = {"hyprpaper": {"ipc_enabled": True}}
            >>> _apply_single_override(settings, "hyprpaper.wallpaper_dirs", ["~/pics"])
            >>> # Result: {"hyprpaper": {"ipc_enabled": True, "wallpaper_dirs": ["~/pics"]}}
        """
        keys = key.split(".")
        target = settings

        # Navigate to the target location, creating dicts as needed
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            elif not isinstance(target[k], dict):
                raise ValueError(
                    f"Cannot navigate through non-dict value at '{k}' in key '{key}'"
                )
            target = target[k]

        final_key = keys[-1]

        # Deep merge if both old and new values are dicts
        if (
            final_key in target
            and isinstance(target[final_key], dict)
            and isinstance(value, dict)
        ):
            target[final_key] = self._deep_merge(target[final_key], value)
        else:
            # Otherwise, replace the value
            target[final_key] = value

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries.

        Recursively merges nested dictionaries. Non-dict values in 'override'
        replace values in 'base'.

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary (new dict, doesn't modify inputs)

        Example:
            >>> base = {"a": 1, "b": {"c": 2, "d": 3}}
            >>> override = {"b": {"d": 4, "e": 5}, "f": 6}
            >>> _deep_merge(base, override)
            {"a": 1, "b": {"c": 2, "d": 4, "e": 5}, "f": 6}
        """
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _load_toml(self, path: Path) -> dict:
        """Load TOML file.

        Args:
            path: Path to TOML file

        Returns:
            Parsed TOML as dictionary

        Raises:
            TOMLOperationError: If loading fails
        """
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            raise TOMLOperationError(f"Failed to load TOML from {path}: {e}")

    def _write_toml(self, path: Path, data: dict) -> None:
        """Write TOML file.

        Args:
            path: Path to TOML file
            data: Data to write

        Raises:
            TOMLOperationError: If writing fails
        """
        try:
            with open(path, "wb") as f:
                tomli_w.dump(data, f)
        except Exception as e:
            raise TOMLOperationError(f"Failed to write TOML to {path}: {e}")

    def _create_backup(self, path: Path) -> Path:
        """Create backup of settings file.

        Args:
            path: Path to file to backup

        Returns:
            Path to backup file (.backup extension)

        Raises:
            TOMLOperationError: If backup creation fails
        """
        backup_path = path.with_suffix(path.suffix + ".backup")
        try:
            shutil.copy2(path, backup_path)
            return backup_path
        except Exception as e:
            raise TOMLOperationError(f"Failed to create backup of {path}: {e}")

    def _rollback(self, original: Path, backup: Path) -> None:
        """Rollback to backup file.

        Args:
            original: Original file path
            backup: Backup file path
        """
        shutil.copy2(backup, original)

    def _validate_settings(
        self,
        settings: dict,
        config_model: type[BaseModel],
    ) -> None:
        """Validate settings against Pydantic model.

        Args:
            settings: Settings dictionary
            config_model: Pydantic model class

        Raises:
            ValidationError: If validation fails
        """
        # Attempt to instantiate the model with the settings
        config_model(**settings)

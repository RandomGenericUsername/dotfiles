import os
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf
from pydantic import ValidationError

from src.config.config import AppConfig as PydanticAppConfig
from src.config.enums import InstallType

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
SETTINGS_FILE = PROJECT_ROOT / "settings.toml"
PROJECT_SETTINGS = (
    PROJECT_ROOT / "src" / "dotfiles-installer" / "config" / "settings.toml"
)

settings_files = [str(SETTINGS_FILE), str(PROJECT_SETTINGS)]


class SettingsModel:
    def __init__(self, settings_files: list[str]):
        self.dynaconf_settings: Dynaconf = Dynaconf(
            settings_files=settings_files,
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
            print("🚨 Configuration Error:")
            print("-" * 40)

            missing_fields = SettingsModel._extract_missing_fields(e)

            if missing_fields:
                print("❌ Missing required fields:")
                for field_path in missing_fields:
                    print(f"   - {field_path}")

                print("\n💡 Add these sections to your settings.toml:")
                toml_suggestions = SettingsModel._generate_toml_suggestions(
                    missing_fields
                )
                print(toml_suggestions)

            # Handle other validation errors
            other_errors = [
                err for err in e.errors() if err["type"] != "missing"
            ]
            if other_errors:
                print("\n❌ Other validation errors:")
                for error in other_errors:
                    field_path = ".".join(str(loc) for loc in error["loc"])
                    print(f"   - {field_path}: {error['msg']}")

            print("\n📁 Settings file locations:")
            print(f"   {SETTINGS_FILE}")

            raise SystemExit(1)

    @staticmethod
    def _extract_missing_fields(
        validation_error: ValidationError,
    ) -> list[str]:
        """Extract missing field paths from validation error."""
        missing_fields = []
        for error in validation_error.errors():
            if error["type"] == "missing":
                field_path = ".".join(str(loc) for loc in error["loc"])
                missing_fields.append(field_path)
        return missing_fields

    @staticmethod
    def _generate_toml_suggestions(missing_fields: list[str]) -> str:
        """Generate TOML configuration suggestions for missing fields."""
        # Group fields by section
        sections = {}

        for field_path in missing_fields:
            parts = field_path.split(".")
            section_path = parts[:-1]
            field_name = parts[-1]

            section_key = ".".join(section_path)
            if section_key not in sections:
                sections[section_key] = []

            sections[section_key].append(field_name)

        # Generate TOML
        toml_lines = []

        for section_path, fields in sections.items():
            toml_lines.append(f"[{section_path}]")

            for field_name in fields:
                full_path = f"{section_path}.{field_name}"
                default_value = SettingsModel._get_default_value_for_field(
                    full_path
                )
                toml_lines.append(f"{field_name} = {default_value}")

            toml_lines.append("")  # Empty line between sections

        return "\n".join(toml_lines)

    @staticmethod
    def _get_default_value_for_field(field_path: str) -> str:
        """Get appropriate default value for a field based on its type."""
        # Define common defaults based on field names and paths
        defaults = {
            "log_level": '"info"',
            "output_to_file": "false",
            "log_directory": '"/tmp/logs"',
            "directory": '"$HOME/.dotfiles"',
            "backup_directory": '"$HOME/.backup"',
            "type": '"update"',
            "hidden": "true",
            "python": '""',
            "nodejs": '""',
            "wallpapers_directory": '"$HOME/wallpapers"',
            "screenshots_directory": '"$HOME/Pictures/Screenshots"',
        }

        field_name = field_path.split(".")[-1]
        return defaults.get(field_name, '"value"')


Settings: PydanticAppConfig = SettingsModel(settings_files=settings_files).settings


def get_settings() -> PydanticAppConfig:
    """Get the application settings."""
    return Settings


def update_settings(
    config: PydanticAppConfig,
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

    # Build update dictionary for install settings
    install_updates = {}
    if install_directory is not None:
        install_updates["directory"] = install_directory
    if backup_directory is not None:
        install_updates["backup_directory"] = backup_directory
    if install_type is not None:
        install_updates["type"] = install_type
    if hide is not None:
        install_updates["hidden"] = hide

    # Add debug updates if any exist
    if debug_updates:
        install_updates["debug"] = config.install.debug.model_copy(
            update=debug_updates
        )

    # Build the main update dictionary
    main_updates = {}
    if install_updates:
        main_updates["install"] = config.install.model_copy(
            update=install_updates
        )

    # Create updated settings
    updated = config.model_copy(update=main_updates)

    return updated

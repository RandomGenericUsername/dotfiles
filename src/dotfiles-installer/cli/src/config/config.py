from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from src.config.defaults import (
    backup_directory,
    install_path,
    log_directory,
    log_level,
    output_to_file,
    screenshots_directory,
    wallpapers_directory,
)
from src.config.enums import InstallType
from src.modules.logging import LogLevels, validate_log_level_string


def validate_boolean_string(value: str | bool) -> bool:
    """
    Validate and convert a string or boolean to bool.

    Args:
        value: String representation of boolean or boolean value

    Returns:
        bool value

    Raises:
        ValueError: If the boolean string is invalid
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized_value = value.lower()
        if normalized_value in ("true", "1", "yes", "on"):
            return True
        elif normalized_value in ("false", "0", "no", "off"):
            return False
        else:
            valid_options = "true, false, 1, 0, yes, no, on, off"
            raise ValueError(
                f"Invalid boolean value '{value}'. Valid options are: {valid_options}"
            )

    raise ValueError(f"Cannot convert {type(value).__name__} to boolean")


class InstallDebugSettings(BaseModel):
    log_level: LogLevels = Field(default=log_level, description="Log level")
    output_to_file: bool = Field(
        default=output_to_file, description="Output log to file"
    )
    log_directory: Path = Field(
        default=log_directory, description="Path to log directory"
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level string matches LogLevelOptions."""
        if isinstance(v, str):
            return validate_log_level_string(v)
        return v

    @field_validator("output_to_file", mode="before")
    @classmethod
    def validate_output_to_file(cls, v):
        """Validate boolean string for output_to_file."""
        return validate_boolean_string(v)


class InstallSettings(BaseModel):

    directory: Path = Field(
        default=install_path, description="Path to install dotfiles"
    )
    backup_directory: Path = Field(
        default=backup_directory, description="Path to the backup directory"
    )
    type: InstallType = Field(
        default=InstallType.update, description="Type of installation"
    )
    hidden: bool = Field(
        default=True, description="Hide the install directory"
    )
    debug: InstallDebugSettings = Field(
        default_factory=InstallDebugSettings, description="Debug settings"
    )

    @field_validator("hidden", mode="before")
    @classmethod
    def validate_hidden(cls, v):
        """Validate boolean string for hidden."""
        return validate_boolean_string(v)


class ProjectPaths(BaseModel):
    wallpapers_directory: Path = Field(
        default=wallpapers_directory,
        description="Path to wallpapers directory",
    )
    screenshots_directory: Path = Field(
        default=screenshots_directory,
        description="Path to screenshots directory",
    )


class Features(BaseModel):
    python: str = Field(
        default="",
        description=(
            "Python version to install via pyenv. see `pyenv install --list`"
        ),
    )
    nodejs: str = Field(
        default="",
        description="Node version to install via nvm. see `nvm ls-remote`",
    )


class DirectoryDeletionSafetySettings(BaseModel):
    """Configuration for safe directory deletion."""

    protected_directories: list[str] = Field(
        default_factory=lambda: [
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
        ],
        description="List of protected directories that should never be deleted",
    )

    dangerous_keywords: list[str] = Field(
        default=["system", "root", "backup", "config"],
        description="Keywords that make a path dangerous to delete",
    )

    minimum_path_depth: int = Field(
        default=3, ge=1, description="Minimum number of path segments required"
    )

    protect_user_homes: bool = Field(
        default=True,
        description="Whether to protect direct user home directories",
    )

    keyword_check_depth_threshold: int = Field(
        default=4,
        ge=2,
        description="Minimum depth for keyword checking "
        "(keywords only checked for shallow paths)",
    )


class SafetySettings(BaseModel):
    """Safety-related configuration settings."""

    directory_deletion: DirectoryDeletionSafetySettings = Field(
        default_factory=DirectoryDeletionSafetySettings,
        description="Directory deletion safety settings",
    )


class AppConfig(BaseModel):
    install: InstallSettings = Field(
        default_factory=InstallSettings, description="Installation settings"
    )
    project_paths: ProjectPaths = Field(
        default_factory=ProjectPaths, description="Project paths"
    )
    features: Features = Field(
        default_factory=Features, description="Features to install"
    )
    safety: SafetySettings = Field(
        default_factory=SafetySettings,
        description="Safety configuration settings",
    )

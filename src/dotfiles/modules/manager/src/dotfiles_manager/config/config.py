"""Configuration models for dotfiles manager."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class ManagerConfig(BaseModel):
    """Configuration for the Manager.

    Attributes:
        data_dir: Directory for storing manager data.
        debug: Enable debug mode.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )

    data_dir: Path = Field(
        default=Path.home() / ".local" / "share" / "dotfiles" / "manager",
        description="Directory for storing manager data",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )


class AppConfig(BaseModel):
    """Application-level configuration.

    Attributes:
        manager: Manager-specific configuration.
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )

    manager: ManagerConfig = Field(
        default_factory=ManagerConfig,
        description="Manager configuration",
    )

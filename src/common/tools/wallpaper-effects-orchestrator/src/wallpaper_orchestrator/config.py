"""Configuration management for wallpaper orchestrator."""

from pathlib import Path
from typing import Any

from dynaconf import Dynaconf
from pydantic import BaseModel, Field


class ContainerConfig(BaseModel):
    """Container configuration."""

    runtime: str = Field(default="docker", description="Container runtime")
    image_name: str = Field(
        default="wallpaper-effects-processor", description="Image name"
    )
    image_tag: str = Field(default="latest", description="Image tag")
    build_no_cache: bool = Field(
        default=False, description="Build without cache"
    )
    build_pull: bool = Field(
        default=True, description="Pull base image during build"
    )


class ProcessingConfig(BaseModel):
    """Processing configuration."""

    mode: str = Field(default="memory", description="Processing mode")
    output_format: str = Field(default="png", description="Output format")
    quality: int = Field(
        default=95, ge=1, le=100, description="Output quality"
    )
    write_metadata: bool = Field(
        default=False, description="Write metadata file"
    )


class BatchConfig(BaseModel):
    """Batch processing configuration."""

    parallel: int = Field(
        default=0, ge=0, description="Number of parallel processes"
    )
    skip_existing: bool = Field(
        default=False, description="Skip existing files"
    )
    continue_on_error: bool = Field(
        default=True, description="Continue on processing errors"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Log level")
    colored: bool = Field(default=True, description="Enable colored output")
    log_file: str = Field(default="", description="Log file path")


class PresetEffect(BaseModel):
    """Effect configuration in preset."""

    name: str = Field(description="Effect name")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Effect parameters"
    )


class Preset(BaseModel):
    """Preset configuration."""

    description: str = Field(description="Preset description")
    effects: list[PresetEffect] = Field(description="Effects to apply")


class AppConfig(BaseModel):
    """Application configuration."""

    container: ContainerConfig = Field(default_factory=ContainerConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    batch: BatchConfig = Field(default_factory=BatchConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    presets: dict[str, Preset] = Field(default_factory=dict)


def load_settings() -> Dynaconf:
    """Load settings from TOML files.

    Returns:
        Dynaconf settings object
    """
    # Get config directory
    config_dir = Path(__file__).parent.parent / "config"
    user_config_dir = (
        Path.home() / ".config" / "wallpaper-effects-orchestrator"
    )

    # Settings files to load
    settings_files = [str(config_dir / "settings.toml")]

    # Add user config if exists
    if user_config_dir.exists():
        user_presets = user_config_dir / "presets.toml"
        if user_presets.exists():
            settings_files.append(str(user_presets))

    # Create Dynaconf instance
    settings = Dynaconf(
        envvar_prefix="WALLPAPER",
        settings_files=settings_files,
        merge_enabled=True,
    )

    return settings


def get_default_config() -> AppConfig:
    """Get default configuration.

    Returns:
        AppConfig with default values
    """
    settings = load_settings()

    # Convert to AppConfig
    config_dict = {
        "container": settings.get("container", {}),
        "processing": settings.get("processing", {}),
        "batch": settings.get("batch", {}),
        "logging": settings.get("logging", {}),
        "presets": {},
    }

    # Load presets
    presets_data = settings.get("presets", {})
    for name, preset_data in presets_data.items():
        config_dict["presets"][name] = Preset(**preset_data)

    return AppConfig(**config_dict)

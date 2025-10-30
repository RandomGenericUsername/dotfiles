"""Wallpaper orchestrator - container-based wallpaper processing tool."""

from wallpaper_orchestrator.config import (
    AppConfig,
    BatchConfig,
    ContainerConfig,
    LoggingConfig,
    Preset,
    PresetEffect,
    ProcessingConfig,
    get_default_config,
    load_settings,
)
from wallpaper_orchestrator.containers import (
    ContainerBuilder,
    ContainerRegistry,
    ContainerRunner,
)
from wallpaper_orchestrator.orchestrator import WallpaperOrchestrator

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Configuration
    "AppConfig",
    "BatchConfig",
    "ContainerConfig",
    "LoggingConfig",
    "Preset",
    "PresetEffect",
    "ProcessingConfig",
    "get_default_config",
    "load_settings",
    # Containers
    "ContainerBuilder",
    "ContainerRegistry",
    "ContainerRunner",
    # Orchestrator
    "WallpaperOrchestrator",
]


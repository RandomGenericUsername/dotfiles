"""Wallpaper Orchestrator - Complete wallpaper setup tool."""

__version__ = "0.1.0"

from wallpaper_orchestrator.config import (
    AppConfig,
    ColorSchemeSettings,
    HyprpaperSettings,
    OrchestratorSettings,
    PipelineSettings,
    WallpaperEffectsSettings,
    load_settings,
)
from wallpaper_orchestrator.orchestrator import WallpaperOrchestrator
from wallpaper_orchestrator.types import WallpaperResult

__all__ = [
    # Version
    "__version__",
    # Main orchestrator
    "WallpaperOrchestrator",
    # Result type
    "WallpaperResult",
    # Configuration
    "AppConfig",
    "OrchestratorSettings",
    "ColorSchemeSettings",
    "WallpaperEffectsSettings",
    "HyprpaperSettings",
    "PipelineSettings",
    "load_settings",
]

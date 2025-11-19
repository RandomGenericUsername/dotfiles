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
from wallpaper_orchestrator.core import (
    WallpaperCacheManager,
    WallpaperOrchestrator,
)
from wallpaper_orchestrator.core.types import WallpaperResult
from wallpaper_orchestrator.integrations import WallpaperProgressSocketManager
from wallpaper_orchestrator.pipeline import (
    GenerateColorSchemeStep,
    GenerateEffectsStep,
    SetWallpaperStep,
)

__all__ = [
    # Version
    "__version__",
    # Main orchestrator
    "WallpaperOrchestrator",
    # Result type
    "WallpaperResult",
    # Cache manager
    "WallpaperCacheManager",
    # Socket manager
    "WallpaperProgressSocketManager",
    # Pipeline steps
    "GenerateColorSchemeStep",
    "GenerateEffectsStep",
    "SetWallpaperStep",
    # Configuration
    "AppConfig",
    "OrchestratorSettings",
    "ColorSchemeSettings",
    "WallpaperEffectsSettings",
    "HyprpaperSettings",
    "PipelineSettings",
    "load_settings",
]

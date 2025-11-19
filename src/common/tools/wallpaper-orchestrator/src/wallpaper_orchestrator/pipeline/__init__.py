"""Pipeline steps for wallpaper orchestration."""

from wallpaper_orchestrator.pipeline.colorscheme_step import (
    GenerateColorSchemeStep,
)
from wallpaper_orchestrator.pipeline.effects_step import GenerateEffectsStep
from wallpaper_orchestrator.pipeline.wallpaper_step import SetWallpaperStep

__all__ = [
    "GenerateEffectsStep",
    "GenerateColorSchemeStep",
    "SetWallpaperStep",
]

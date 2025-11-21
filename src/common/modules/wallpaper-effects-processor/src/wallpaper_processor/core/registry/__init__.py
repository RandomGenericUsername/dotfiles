"""Registry module for dynamic effect discovery."""

from wallpaper_processor.core.registry.decorators import register_effect
from wallpaper_processor.core.registry.effect_registry import EffectRegistry

__all__ = [
    "EffectRegistry",
    "register_effect",
]

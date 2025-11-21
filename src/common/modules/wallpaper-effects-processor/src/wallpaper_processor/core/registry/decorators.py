"""Decorators for effect registration."""

from typing import TYPE_CHECKING, Type, TypeVar

if TYPE_CHECKING:
    from wallpaper_processor.core.base import WallpaperEffect

from wallpaper_processor.core.registry.effect_registry import EffectRegistry

T = TypeVar("T", bound="WallpaperEffect")


def register_effect(effect_name: str) -> callable:
    """Decorator to register an effect implementation.

    This decorator automatically registers effect classes with the registry
    based on their backend_name property.

    Args:
        effect_name: Name of the effect (e.g., "blur", "brightness")

    Returns:
        Decorator function

    Example:
        @register_effect("blur")
        class ImageMagickBlur(WallpaperEffect):
            @property
            def backend_name(self) -> str:
                return "imagemagick"
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Create a temporary instance to get backend_name
        # This is safe because WallpaperEffect.__init__ takes no required args
        temp_instance = cls()
        backend_name = temp_instance.backend_name

        # Register the effect
        EffectRegistry.register_effect(effect_name, backend_name, cls)

        return cls

    return decorator

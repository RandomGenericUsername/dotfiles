"""Effect registry for dynamic effect discovery and registration."""

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from wallpaper_processor.core.base import WallpaperEffect
    from wallpaper_processor.core.types import EffectParams


class EffectRegistry:
    """Central registry for wallpaper effects and their parameters.

    This registry enables dynamic effect discovery without hardcoded lists.
    Effects register themselves using the @register_effect decorator.
    """

    # Registry storage
    # Format: {effect_name: {backend_name: EffectClass}}
    _effects: dict[str, dict[str, Type["WallpaperEffect"]]] = {}

    # Format: {effect_name: ParamsClass}
    _params: dict[str, Type["EffectParams"]] = {}

    @classmethod
    def register_effect(
        cls,
        effect_name: str,
        backend_name: str,
        effect_class: Type["WallpaperEffect"],
    ) -> None:
        """Register an effect implementation.

        Args:
            effect_name: Name of the effect (e.g., "blur", "brightness")
            backend_name: Backend name (e.g., "imagemagick", "pil")
            effect_class: The effect class to register
        """
        if effect_name not in cls._effects:
            cls._effects[effect_name] = {}

        cls._effects[effect_name][backend_name] = effect_class

    @classmethod
    def register_params(
        cls,
        effect_name: str,
        params_class: Type["EffectParams"],
    ) -> None:
        """Register effect parameters class.

        Args:
            effect_name: Name of the effect
            params_class: The parameters class to register
        """
        cls._params[effect_name] = params_class

    @classmethod
    def get_effect_class(
        cls,
        effect_name: str,
        backend_name: str,
    ) -> Type["WallpaperEffect"] | None:
        """Get effect class for given effect and backend.

        Args:
            effect_name: Name of the effect
            backend_name: Backend name

        Returns:
            Effect class or None if not found
        """
        return cls._effects.get(effect_name, {}).get(backend_name)

    @classmethod
    def get_params_class(
        cls,
        effect_name: str,
    ) -> Type["EffectParams"] | None:
        """Get parameters class for given effect.

        Args:
            effect_name: Name of the effect

        Returns:
            Parameters class or None if not found
        """
        return cls._params.get(effect_name)

    @classmethod
    def get_all_effect_names(cls) -> list[str]:
        """Get list of all registered effect names.

        Returns:
            Sorted list of effect names
        """
        return sorted(cls._effects.keys())

    @classmethod
    def get_backends_for_effect(cls, effect_name: str) -> list[str]:
        """Get list of available backends for an effect.

        Args:
            effect_name: Name of the effect

        Returns:
            List of backend names
        """
        return list(cls._effects.get(effect_name, {}).keys())

    @classmethod
    def is_effect_registered(cls, effect_name: str) -> bool:
        """Check if an effect is registered.

        Args:
            effect_name: Name of the effect

        Returns:
            True if effect is registered
        """
        return effect_name in cls._effects

    @classmethod
    def clear(cls) -> None:
        """Clear all registrations (mainly for testing)."""
        cls._effects.clear()
        cls._params.clear()

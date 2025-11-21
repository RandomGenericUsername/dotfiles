"""Effects cache query utilities."""

from pathlib import Path


def get_available_effects(wallpaper_name: str, effects_cache_dir: Path) -> list[str]:
    """Get list of effects that exist for a wallpaper.

    This function queries the effects cache directory to find all generated
    effects for a specific wallpaper. Effects are stored as PNG files in
    subdirectories named after the wallpaper.

    Args:
        wallpaper_name: Name of the wallpaper (without extension)
        effects_cache_dir: Effects cache directory

    Returns:
        Sorted list of effect names (without .png extension)

    Example:
        >>> get_available_effects("mountain", Path("~/.cache/wallpaper-effects"))
        ['blur', 'grayscale', 'pixelate']
    """
    wallpaper_effects_dir = effects_cache_dir / wallpaper_name

    if not wallpaper_effects_dir.exists():
        return []

    effects = []
    for effect_file in wallpaper_effects_dir.glob("*.png"):
        effect_name = effect_file.stem
        effects.append(effect_name)

    return sorted(effects)

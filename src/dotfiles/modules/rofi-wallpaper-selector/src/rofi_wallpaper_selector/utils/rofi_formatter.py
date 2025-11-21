"""Rofi output formatting utilities."""


def format_rofi_item(label: str, icon_path: str | None) -> str:
    """Format item for rofi with icon.

    Args:
        label: Item label
        icon_path: Path to icon image (or None for no icon)

    Returns:
        Formatted string for rofi

    Example:
        >>> format_rofi_item("wallpaper1", "/path/to/wallpaper1.png")
        'wallpaper1\\x00icon\\x1f/path/to/wallpaper1.png'
        >>> format_rofi_item("off", None)
        'off'
    """
    if icon_path:
        # Format: label\x00icon\x1f/path/to/icon
        return f"{label}\x00icon\x1f{icon_path}"
    else:
        return label

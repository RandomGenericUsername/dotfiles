"""Hook-related models."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class HookContext:
    """Context passed to hooks during execution.

    Attributes:
        wallpaper_path: Path to wallpaper being processed
        colorscheme_files: Dict of format -> path (e.g., {"json": Path(...), "css": Path(...)})
        font_family: System font family
        font_size: System font size in pixels
        monitor: Monitor name the wallpaper is for
        from_cache: Whether wallpaper was loaded from cache
        config: Hook-specific configuration from settings.toml
    """

    wallpaper_path: Path
    colorscheme_files: dict[str, Path]
    font_family: str
    font_size: int
    monitor: str
    from_cache: bool
    config: dict


@dataclass
class HookResult:
    """Result of hook execution.

    Attributes:
        success: Whether hook executed successfully
        message: Human-readable message
        data: Optional data returned by hook
    """

    success: bool
    message: str
    data: dict | None = None

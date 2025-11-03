"""Custom exceptions for wallpaper processor."""


class WallpaperProcessorError(Exception):
    """Base exception for wallpaper processor."""

    pass


class EffectNotAvailableError(WallpaperProcessorError):
    """Raised when an effect's dependencies are not available."""

    def __init__(self, effect_name: str, message: str | None = None):
        """Initialize exception.

        Args:
            effect_name: Name of the unavailable effect
            message: Optional custom message
        """
        self.effect_name = effect_name
        if message is None:
            message = f"Effect '{effect_name}' is not available"
        super().__init__(message)


class InvalidParametersError(WallpaperProcessorError):
    """Raised when effect parameters are invalid."""

    pass


class PresetNotFoundError(WallpaperProcessorError):
    """Raised when a preset is not found."""

    def __init__(self, preset_name: str):
        """Initialize exception.

        Args:
            preset_name: Name of the preset that was not found
        """
        self.preset_name = preset_name
        super().__init__(f"Preset '{preset_name}' not found")


class ProcessingError(WallpaperProcessorError):
    """Raised when image processing fails."""

    pass


class UnsupportedFormatError(WallpaperProcessorError):
    """Raised when an image format is not supported."""

    def __init__(self, format_name: str):
        """Initialize exception.

        Args:
            format_name: Name of the unsupported format
        """
        self.format_name = format_name
        super().__init__(f"Format '{format_name}' is not supported")

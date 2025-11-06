"""Custom exceptions for hyprpaper operations."""


class HyprpaperError(Exception):
    """Base exception for hyprpaper operations."""

    pass


class HyprpaperNotRunningError(HyprpaperError):
    """Raised when hyprpaper is not running."""

    pass


class HyprpaperIPCError(HyprpaperError):
    """Raised when IPC communication fails."""

    def __init__(
        self,
        message: str,
        command: str | None = None,
        exit_code: int | None = None,
    ):
        """Initialize IPC error.

        Args:
            message: Error message
            command: Command that failed (optional)
            exit_code: Exit code of failed command (optional)
        """
        self.command = command
        self.exit_code = exit_code
        super().__init__(message)


class WallpaperNotFoundError(HyprpaperError):
    """Raised when wallpaper file doesn't exist."""

    pass


class MonitorNotFoundError(HyprpaperError):
    """Raised when monitor doesn't exist."""

    pass


class WallpaperNotLoadedError(HyprpaperError):
    """Raised when trying to use unloaded wallpaper."""

    pass


class WallpaperTooLargeError(HyprpaperError):
    """Raised when wallpaper exceeds maximum allowed size."""

    def __init__(
        self,
        message: str,
        wallpaper_size_mb: float | None = None,
        max_allowed_mb: float | None = None,
    ):
        """Initialize wallpaper too large error.

        Args:
            message: Error message
            wallpaper_size_mb: Size of wallpaper in MB (optional)
            max_allowed_mb: Maximum allowed size in MB (optional)
        """
        self.wallpaper_size_mb = wallpaper_size_mb
        self.max_allowed_mb = max_allowed_mb
        super().__init__(message)

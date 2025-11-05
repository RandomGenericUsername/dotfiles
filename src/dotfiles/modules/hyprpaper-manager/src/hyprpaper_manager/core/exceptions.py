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

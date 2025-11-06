"""IPC client for hyprpaper via hyprctl."""

import subprocess
from pathlib import Path

from hyprpaper_manager.core.exceptions import (
    HyprpaperIPCError,
    HyprpaperNotRunningError,
)


class HyprpaperIPC:
    """IPC client for hyprpaper via hyprctl."""

    def __init__(self, timeout: int = 5):
        """Initialize IPC client.

        Args:
            timeout: Command timeout in seconds
        """
        self.timeout = timeout

    def is_running(self) -> bool:
        """Check if hyprpaper is running."""
        try:
            result = subprocess.run(
                ["pgrep", "-x", "hyprpaper"],
                capture_output=True,
                timeout=self.timeout,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _execute(self, command: str, *args: str) -> str:
        """Execute hyprctl hyprpaper command.

        Args:
            command: Command name (preload, wallpaper, etc.)
            *args: Command arguments

        Returns:
            Command output

        Raises:
            HyprpaperNotRunningError: If hyprpaper is not running
            HyprpaperIPCError: If command fails
        """
        if not self.is_running():
            raise HyprpaperNotRunningError(
                "hyprpaper is not running. Start it with 'hyprpaper &'"
            )

        cmd = ["hyprctl", "hyprpaper", command, *args]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True,
            )
            return result.stdout.strip()

        except subprocess.TimeoutExpired as e:
            raise HyprpaperIPCError(
                f"Command timed out after {self.timeout}s",
                command=" ".join(cmd),
            ) from e

        except subprocess.CalledProcessError as e:
            raise HyprpaperIPCError(
                f"Command failed: {e.stderr}",
                command=" ".join(cmd),
                exit_code=e.returncode,
            ) from e

        except FileNotFoundError as e:
            raise HyprpaperIPCError(
                "hyprctl not found. Is Hyprland installed?",
                command="hyprctl",
            ) from e

    def preload(self, wallpaper: Path) -> None:
        """Preload wallpaper into memory."""
        self._execute("preload", str(wallpaper))

    def wallpaper(
        self, monitor: str, wallpaper: Path, mode: str | None = None
    ) -> None:
        """Set wallpaper for monitor."""
        path_str = str(wallpaper)
        if mode:
            path_str = f"{mode}:{path_str}"
        self._execute("wallpaper", f"{monitor},{path_str}")

    def unload(self, target: Path | str) -> None:
        """Unload wallpaper(s) from memory.

        Args:
            target: Wallpaper path, "all", or "unused"
        """
        self._execute("unload", str(target))

    def reload(
        self, monitor: str, wallpaper: Path, mode: str | None = None
    ) -> None:
        """Quick reload wallpaper (auto preload/unload)."""
        path_str = str(wallpaper)
        if mode:
            path_str = f"{mode}:{path_str}"
        self._execute("reload", f"{monitor},{path_str}")

    def listloaded(self) -> list[Path]:
        """List loaded wallpapers."""
        output = self._execute("listloaded")
        if not output or output == "no wallpapers loaded":
            return []
        return [
            Path(line.strip())
            for line in output.split("\n")
            if line.strip() and line.strip() != "no wallpapers loaded"
        ]

    def listactive(self) -> dict[str, Path]:
        """List active wallpapers per monitor."""
        output = self._execute("listactive")
        if not output or output == "no wallpapers active":
            return {}
        result = {}
        for line in output.split("\n"):
            if "=" in line:
                monitor, wallpaper = line.split("=", 1)
                result[monitor.strip()] = Path(wallpaper.strip())
        return result

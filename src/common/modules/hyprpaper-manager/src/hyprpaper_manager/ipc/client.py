"""IPC client for hyprpaper via hyprctl."""

import logging
import subprocess
import time
from pathlib import Path

from hyprpaper_manager.core.exceptions import (
    HyprpaperIPCError,
    HyprpaperNotRunningError,
)

logger = logging.getLogger(__name__)


class HyprpaperIPC:
    """IPC client for hyprpaper via hyprctl.

    This client handles communication with hyprpaper via hyprctl commands,
    with built-in retry logic and socket readiness checking to handle
    startup race conditions.

    Args:
        timeout: Default command timeout in seconds
        retry_attempts: Number of retry attempts for transient failures
        retry_delay: Initial delay between retries (exponential backoff)
        startup_wait: Maximum time to wait for socket on startup
    """

    def __init__(
        self,
        timeout: int = 5,
        retry_attempts: int = 3,
        retry_delay: float = 0.5,
        startup_wait: float = 2.0,
    ):
        """Initialize IPC client.

        Args:
            timeout: Default command timeout in seconds
            retry_attempts: Number of retry attempts for transient failures
            retry_delay: Initial delay between retries in seconds
            startup_wait: Maximum time to wait for socket on startup
        """
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.startup_wait = startup_wait
        logger.debug(
            f"Initialized HyprpaperIPC: timeout={timeout}s, "
            f"retry_attempts={retry_attempts}, retry_delay={retry_delay}s, "
            f"startup_wait={startup_wait}s"
        )

    def is_running(self) -> bool:
        """Check if hyprpaper process is running.

        Note: This only checks if the process exists, not if the IPC socket
        is ready. Use is_ready() to check if the socket is ready for commands.

        Returns:
            True if hyprpaper process exists
        """
        try:
            result = subprocess.run(
                ["pgrep", "-x", "hyprpaper"],
                capture_output=True,
                timeout=self.timeout,
            )
            is_running = result.returncode == 0
            logger.debug(f"hyprpaper process running: {is_running}")
            return is_running
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.debug(f"Error checking if hyprpaper is running: {e}")
            return False

    def is_ready(self, max_wait: float | None = None) -> bool:
        """Check if hyprpaper IPC socket is ready for commands.

        This method handles the race condition where hyprpaper process exists
        but the IPC socket isn't ready yet. It will wait up to max_wait seconds
        for the socket to become ready.

        Args:
            max_wait: Maximum time to wait for socket
                     (uses startup_wait if None)

        Returns:
            True if socket is ready and accepting commands
        """
        if max_wait is None:
            max_wait = self.startup_wait

        if not self.is_running():
            logger.debug("hyprpaper not running, socket not ready")
            return False

        logger.debug(
            f"Checking if hyprpaper socket is ready (max_wait={max_wait}s)"
        )
        start_time = time.time()
        attempt = 0

        while time.time() - start_time < max_wait:
            attempt += 1

            # Re-check if process is still running before each attempt
            if not self.is_running():
                logger.debug(
                    f"hyprpaper process died during socket wait "
                    f"(after {attempt} attempts)"
                )
                return False

            try:
                # Try a simple test command to check socket readiness
                result = subprocess.run(
                    ["hyprctl", "hyprpaper", "listloaded"],
                    capture_output=True,
                    text=True,
                    timeout=1,
                    check=False,  # Don't raise on error
                )

                if result.returncode == 0:
                    elapsed = time.time() - start_time
                    logger.debug(
                        f"hyprpaper socket ready after {elapsed:.2f}s "
                        f"({attempt} attempts)"
                    )
                    return True

                logger.debug(
                    f"Socket not ready (attempt {attempt}): "
                    f"returncode={result.returncode}"
                )

            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                logger.debug(f"Socket check failed (attempt {attempt}): {e}")

            # Wait before next attempt
            time.sleep(0.1)

        elapsed = time.time() - start_time
        logger.warning(
            f"hyprpaper socket not ready after {elapsed:.2f}s "
            f"({attempt} attempts)"
        )
        return False

    def _execute(
        self,
        command: str,
        *args: str,
        timeout: int | None = None,
        retry: bool = True,
    ) -> str:
        """Execute hyprctl hyprpaper command with retry logic.

        This method includes:
        - Socket readiness checking to handle startup race conditions
        - Automatic retry with exponential backoff for transient failures
        - Improved error messages with context

        Args:
            command: Command name (preload, wallpaper, etc.)
            *args: Command arguments
            timeout: Command timeout in seconds (uses default if None)
            retry: Whether to retry on transient failures

        Returns:
            Command output

        Raises:
            HyprpaperNotRunningError: If hyprpaper is not running
            HyprpaperIPCError: If command fails after retries
        """
        if timeout is None:
            timeout = self.timeout

        # Check if socket is ready (this also checks if process is running)
        if not self.is_ready():
            # Re-check process to provide better error message
            if not self.is_running():
                logger.error("hyprpaper process not running")
                raise HyprpaperNotRunningError(
                    "hyprpaper is not running. Start it with 'hyprpaper &'"
                )
            else:
                logger.error("hyprpaper socket not ready")
                raise HyprpaperIPCError(
                    "hyprpaper IPC socket is not ready. "
                    "The process may be starting up or experiencing issues.",
                    command=f"hyprctl hyprpaper {command}",
                )

        cmd = ["hyprctl", "hyprpaper", command, *args]
        cmd_str = " ".join(cmd)
        logger.debug(f"Executing: {cmd_str}")

        # Retry loop
        max_attempts = self.retry_attempts if retry else 1
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=True,
                )
                output = result.stdout.strip()
                logger.debug(
                    f"Command succeeded (attempt {attempt}/{max_attempts}): "
                    f"{output[:100]}"
                )
                return output

            except subprocess.TimeoutExpired as e:
                logger.warning(
                    f"Command timed out after {timeout}s "
                    f"(attempt {attempt}/{max_attempts})"
                )
                last_error = HyprpaperIPCError(
                    f"Command timed out after {timeout}s",
                    command=cmd_str,
                )
                if attempt < max_attempts:
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.debug(f"Retrying after {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                raise last_error from e

            except subprocess.CalledProcessError as e:
                stderr = e.stderr.strip() if e.stderr else ""

                # Provide context-aware error messages
                if not stderr:
                    # Empty stderr often means socket isn't ready
                    if not self.is_ready(max_wait=0.1):
                        stderr = (
                            "hyprpaper IPC socket not responding "
                            "(process may be starting or crashed)"
                        )
                    else:
                        stderr = "Command failed with no error output"

                logger.warning(
                    f"Command failed: {stderr} "
                    f"(attempt {attempt}/{max_attempts}, "
                    f"exit_code={e.returncode})"
                )

                last_error = HyprpaperIPCError(
                    f"Command failed: {stderr}",
                    command=cmd_str,
                    exit_code=e.returncode,
                )

                # Retry on transient errors
                if attempt < max_attempts and retry:
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.debug(f"Retrying after {delay:.2f}s...")
                    time.sleep(delay)
                    continue

                raise last_error from e

            except FileNotFoundError as e:
                logger.error("hyprctl command not found")
                raise HyprpaperIPCError(
                    "hyprctl not found. Is Hyprland installed?",
                    command="hyprctl",
                ) from e

        # Should never reach here, but just in case
        if last_error:
            raise last_error
        raise HyprpaperIPCError(
            f"Command failed after {max_attempts} attempts",
            command=cmd_str,
        )

    def preload(self, wallpaper: Path, timeout: int | None = None) -> None:
        """Preload wallpaper into memory.

        Args:
            wallpaper: Path to wallpaper file
            timeout: Command timeout in seconds (uses default if None)

        Raises:
            HyprpaperNotRunningError: If hyprpaper is not running
            HyprpaperIPCError: If command fails
        """
        self._execute("preload", str(wallpaper), timeout=timeout)

    def wallpaper(
        self,
        monitor: str,
        wallpaper: Path,
        mode: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Set wallpaper for monitor.

        Args:
            monitor: Monitor name (empty string for all monitors)
            wallpaper: Path to wallpaper file
            mode: Display mode (cover, contain, tile) - optional
            timeout: Command timeout in seconds (uses default if None)

        Raises:
            HyprpaperNotRunningError: If hyprpaper is not running
            HyprpaperIPCError: If command fails
        """
        path_str = str(wallpaper)
        if mode:
            path_str = f"{mode}:{path_str}"
        self._execute("wallpaper", f"{monitor},{path_str}", timeout=timeout)

    def unload(self, target: Path | str, timeout: int | None = None) -> None:
        """Unload wallpaper(s) from memory.

        Args:
            target: Wallpaper path, "all", or "unused"
            timeout: Command timeout in seconds (uses default if None)

        Raises:
            HyprpaperNotRunningError: If hyprpaper is not running
            HyprpaperIPCError: If command fails
        """
        self._execute("unload", str(target), timeout=timeout)

    def reload(
        self,
        monitor: str,
        wallpaper: Path,
        mode: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Quick reload wallpaper (auto preload/unload).

        Args:
            monitor: Monitor name (empty string for all monitors)
            wallpaper: Path to wallpaper file
            mode: Display mode (cover, contain, tile) - optional
            timeout: Command timeout in seconds (uses default if None)

        Raises:
            HyprpaperNotRunningError: If hyprpaper is not running
            HyprpaperIPCError: If command fails
        """
        path_str = str(wallpaper)
        if mode:
            path_str = f"{mode}:{path_str}"
        self._execute("reload", f"{monitor},{path_str}", timeout=timeout)

    def listloaded(self, timeout: int | None = None) -> list[Path]:
        """List loaded wallpapers.

        Args:
            timeout: Command timeout in seconds (uses default if None)

        Returns:
            List of loaded wallpaper paths

        Raises:
            HyprpaperNotRunningError: If hyprpaper is not running
            HyprpaperIPCError: If command fails
        """
        output = self._execute("listloaded", timeout=timeout)
        if not output or output == "no wallpapers loaded":
            return []
        return [
            Path(line.strip())
            for line in output.split("\n")
            if line.strip() and line.strip() != "no wallpapers loaded"
        ]

    def listactive(self, timeout: int | None = None) -> dict[str, Path]:
        """List active wallpapers per monitor.

        Args:
            timeout: Command timeout in seconds (uses default if None)

        Returns:
            Dictionary mapping monitor names to wallpaper paths

        Raises:
            HyprpaperNotRunningError: If hyprpaper is not running
            HyprpaperIPCError: If command fails
        """
        output = self._execute("listactive", timeout=timeout)
        if not output or output == "no wallpapers active":
            return {}
        result = {}
        for line in output.split("\n"):
            if "=" in line:
                monitor, wallpaper = line.split("=", 1)
                result[monitor.strip()] = Path(wallpaper.strip())
        return result

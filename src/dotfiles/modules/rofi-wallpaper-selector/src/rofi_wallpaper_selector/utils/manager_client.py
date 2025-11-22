"""Client for interacting with dotfiles-manager."""

import json
import subprocess
from pathlib import Path


class ManagerClient:
    """Client for interacting with dotfiles-manager via CLI.

    This client calls the manager's CLI commands as subprocesses
    to avoid dependency conflicts between venvs.
    """

    def __init__(self, manager_cli: Path):
        """Initialize manager client.

        Args:
            manager_cli: Path to dotfiles-manager CLI executable
        """
        self.manager_cli = manager_cli

        if not self.manager_cli.exists():
            raise FileNotFoundError(
                f"Manager CLI not found at {self.manager_cli}. "
                "Make sure dotfiles-manager is installed."
            )

    def get_current_wallpaper_state(self, monitor: str) -> dict | None:
        """Get current wallpaper state for monitor.

        Args:
            monitor: Monitor name (e.g., "default", "focused", "DP-1")

        Returns:
            Dict with wallpaper state including:
            - monitor: Monitor name
            - wallpaper_path: Path to current wallpaper (could be effect variant)
            - original_wallpaper_path: Path to original wallpaper
            - current_effect: Name of current effect ("off" for original)
            - last_changed: ISO timestamp
            - from_cache: Boolean
            Returns None if not set.

        Note:
            If the specified monitor has no wallpaper set, this will fall back
            to returning the wallpaper from any monitor that has one set.
        """
        # Try the get-wallpaper-state command (JSON output)
        try:
            result = subprocess.run(
                [str(self.manager_cli), "get-wallpaper-state", monitor],
                capture_output=True,
                text=True,
                check=True,
            )

            # The command outputs JSON
            state_json = result.stdout.strip()
            if state_json:
                state = json.loads(state_json)
                # Convert path strings to Path objects
                state["wallpaper_path"] = Path(state["wallpaper_path"])
                state["original_wallpaper_path"] = Path(
                    state["original_wallpaper_path"]
                )
                return state

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            # Command failed, try fallback to default monitor
            try:
                result = subprocess.run(
                    [str(self.manager_cli), "get-wallpaper-state", "default"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                state_json = result.stdout.strip()
                if state_json:
                    state = json.loads(state_json)
                    # Convert path strings to Path objects
                    state["wallpaper_path"] = Path(state["wallpaper_path"])
                    state["original_wallpaper_path"] = Path(
                        state["original_wallpaper_path"]
                    )
                    return state

            except (subprocess.CalledProcessError, json.JSONDecodeError):
                pass

        return None

    def get_current_wallpaper(self, monitor: str) -> Path | None:
        """Get current wallpaper for monitor.

        Args:
            monitor: Monitor name (e.g., "default", "focused", "DP-1")

        Returns:
            Path to current wallpaper, or None if not set

        Note:
            If the specified monitor has no wallpaper set, this will fall back
            to returning the wallpaper from any monitor that has one set.
            This handles cases where the monitor name doesn't match exactly
            (e.g., "focused" vs "default").
        """
        # Try the new get-wallpaper command first (machine-readable output)
        try:
            result = subprocess.run(
                [str(self.manager_cli), "get-wallpaper", monitor],
                capture_output=True,
                text=True,
                check=True,
            )

            # The command outputs just the path
            wallpaper_path = result.stdout.strip()
            if wallpaper_path:
                return Path(wallpaper_path)

        except subprocess.CalledProcessError:
            # Command failed, try fallback to default monitor
            try:
                result = subprocess.run(
                    [str(self.manager_cli), "get-wallpaper", "default"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                wallpaper_path = result.stdout.strip()
                if wallpaper_path:
                    return Path(wallpaper_path)

            except subprocess.CalledProcessError:
                pass

        return None

    def change_wallpaper(
        self,
        wallpaper_path: Path,
        monitor: str,
        generate_colorscheme: bool = True,
        generate_effects: bool = True,
    ) -> dict:
        """Change wallpaper.

        Args:
            wallpaper_path: Path to wallpaper image
            monitor: Monitor name
            generate_colorscheme: Whether to generate colorscheme
            generate_effects: Whether to generate effects

        Returns:
            Result dictionary with success status
        """
        # Build command
        cmd = [
            str(self.manager_cli),
            "change-wallpaper",
            str(wallpaper_path),
            "--monitor",
            monitor,
        ]

        # Add colorscheme flag
        if generate_colorscheme:
            cmd.append("--colorscheme")
        else:
            cmd.append("--no-colorscheme")

        # Add effects flag
        if generate_effects:
            cmd.append("--effects")
        else:
            cmd.append("--no-effects")

        # Execute command
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            return {
                "success": True,
                "wallpaper_path": wallpaper_path,
                "monitor": monitor,
                "output": result.stdout,
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": str(e),
                "stderr": e.stderr,
            }

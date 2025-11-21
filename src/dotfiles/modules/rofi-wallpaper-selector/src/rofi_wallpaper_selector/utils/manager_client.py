"""Client for interacting with dotfiles-manager."""

import subprocess
from pathlib import Path


class ManagerClient:
    """Client for interacting with dotfiles-manager via CLI.

    This client calls the manager's CLI commands as subprocesses
    to avoid dependency conflicts between venvs.
    """

    def __init__(self, manager_path: Path):
        """Initialize manager client.

        Args:
            manager_path: Path to dotfiles-manager module
        """
        self.manager_path = manager_path
        self.manager_cli = manager_path / ".venv" / "bin" / "dotfiles-manager"

        if not self.manager_cli.exists():
            raise FileNotFoundError(
                f"Manager CLI not found at {self.manager_cli}. "
                "Make sure dotfiles-manager is installed."
            )

    def get_current_wallpaper(self, monitor: str) -> Path | None:
        """Get current wallpaper for monitor.

        Args:
            monitor: Monitor name

        Returns:
            Path to current wallpaper, or None if not set
        """
        # Call: dotfiles-manager status --monitor <monitor>
        # Parse output to extract wallpaper path
        try:
            result = subprocess.run(
                [str(self.manager_cli), "status", "--monitor", monitor],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the output to find wallpaper path
            # The status command outputs a table, we need to extract the wallpaper path
            # Format: "│ Monitor │ Wallpaper │ Last Changed │"
            # We'll look for lines containing the monitor name
            for line in result.stdout.split("\n"):
                if (
                    monitor in line
                    and "Not set" not in line
                    and "Monitor" not in line
                ):
                    # Extract path from the line
                    # Split by │ and get the wallpaper column (index 2)
                    parts = [p.strip() for p in line.split("│")]
                    if (
                        len(parts) >= 4
                    ):  # Should have: '', 'Monitor', 'Wallpaper', 'Last Changed', ''
                        wallpaper_str = parts[2].strip()
                        if wallpaper_str and wallpaper_str != "Wallpaper":
                            return Path(wallpaper_str)

            return None

        except subprocess.CalledProcessError:
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

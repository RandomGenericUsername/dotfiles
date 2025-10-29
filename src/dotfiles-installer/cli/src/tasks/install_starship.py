"""Starship prompt installer utilities."""

import subprocess


class StarshipInstallError(Exception):
    """Exception raised when Starship installation fails."""

    def __init__(
        self,
        message: str,
        command: str | None = None,
        exit_code: int | None = None,
    ):
        """
        Initialize the error.

        Args:
            message: Error message
            command: Command that failed (optional)
            exit_code: Exit code of failed command (optional)
        """
        self.message = message
        self.command = command
        self.exit_code = exit_code
        super().__init__(message)


def check_starship_installed() -> bool:
    """
    Check if Starship is already installed.

    Returns:
        True if starship command is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["starship", "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_starship(force: bool = False, timeout: int = 300) -> None:
    """
    Install Starship prompt using the official installation script.

    Downloads and executes: curl -sS https://starship.rs/install.sh | sh

    Args:
        force: Force reinstallation even if already installed
        timeout: Installation timeout in seconds (default: 300)

    Raises:
        StarshipInstallError: If installation fails
    """
    # Check if already installed
    if not force and check_starship_installed():
        return

    try:
        # Download the installation script
        curl_result = subprocess.run(
            ["curl", "-sS", "https://starship.rs/install.sh"],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )

        # Execute the installation script with sh
        # The -s flag makes the script non-interactive (accepts defaults)
        subprocess.run(
            ["sh", "-s", "--", "-y"],
            input=curl_result.stdout,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )

        # Verify installation succeeded
        if not check_starship_installed():
            raise StarshipInstallError(
                "Starship installation completed but starship command "
                "not found. You may need to add ~/.cargo/bin to your PATH."
            )

    except subprocess.TimeoutExpired as e:
        raise StarshipInstallError(
            f"Starship installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise StarshipInstallError(
            f"Starship installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e

    except FileNotFoundError as e:
        raise StarshipInstallError(
            "curl command not found. Please install curl first.",
            command="curl",
        ) from e


def get_starship_version() -> str | None:
    """
    Get the installed Starship version.

    Returns:
        Version string if installed, None otherwise
    """
    try:
        result = subprocess.run(
            ["starship", "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        # Output format: "starship 1.x.x"
        # Extract just the version number
        version_line = result.stdout.strip()
        if version_line.startswith("starship "):
            return version_line.split()[1]
        return version_line
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None

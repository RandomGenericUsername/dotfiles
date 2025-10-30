"""Oh My Zsh installer utilities."""

import os
import subprocess
from pathlib import Path


class OhMyZshInstallError(Exception):
    """Exception raised when Oh My Zsh installation fails."""

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


def check_oh_my_zsh_installed(oh_my_zsh_dir: Path) -> bool:
    """
    Check if Oh My Zsh is already installed.

    Args:
        oh_my_zsh_dir: Directory where Oh My Zsh should be installed

    Returns:
        True if Oh My Zsh is installed, False otherwise
    """
    # Check for oh-my-zsh.sh file which is the main script
    oh_my_zsh_script = oh_my_zsh_dir / "oh-my-zsh.sh"
    return oh_my_zsh_script.exists()


def install_oh_my_zsh(
    oh_my_zsh_dir: Path,
    force: bool = False,
    timeout: int = 300,
) -> None:
    """
    Install Oh My Zsh using the official installation script.

    Downloads and executes the Oh My Zsh installation script with custom directory.
    Sets ZSH environment variable to override default installation location.

    Args:
        oh_my_zsh_dir: Directory where Oh My Zsh should be installed
        force: Force reinstallation even if already installed
        timeout: Installation timeout in seconds (default: 300)

    Raises:
        OhMyZshInstallError: If installation fails
    """
    # Check if already installed
    if not force and check_oh_my_zsh_installed(oh_my_zsh_dir):
        return

    # Ensure parent directory exists
    oh_my_zsh_dir.parent.mkdir(parents=True, exist_ok=True)

    # Remove empty oh-my-zsh directory if it exists (created by PathsBuilder.create())
    # The Oh My Zsh installer will fail if the directory already exists
    if oh_my_zsh_dir.exists() and not any(oh_my_zsh_dir.iterdir()):
        oh_my_zsh_dir.rmdir()

    try:
        # Download the installation script
        install_url = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"

        curl_result = subprocess.run(
            ["curl", "-fsSL", install_url],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )

        # Execute the installation script with custom ZSH directory
        # The script respects the ZSH environment variable
        # --unattended flag skips interactive prompts
        subprocess.run(
            ["sh", "-s", "--", "--unattended"],
            input=curl_result.stdout,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
            env={
                **os.environ,
                "ZSH": str(oh_my_zsh_dir),
            },
        )

        # Verify installation succeeded
        if not check_oh_my_zsh_installed(oh_my_zsh_dir):
            raise OhMyZshInstallError(
                f"Oh My Zsh installation completed but oh-my-zsh.sh not found in {oh_my_zsh_dir}. "
                "Installation may have failed."
            )

    except subprocess.TimeoutExpired as e:
        raise OhMyZshInstallError(
            f"Oh My Zsh installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = (
            e.stderr
            if e.stderr
            else f"Unknown error (stdout: {e.stdout[:200] if e.stdout else 'empty'})"
        )
        raise OhMyZshInstallError(
            f"Oh My Zsh installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e

    except FileNotFoundError as e:
        raise OhMyZshInstallError(
            "curl command not found. Please install curl first.",
            command="curl",
        ) from e


def get_oh_my_zsh_version(oh_my_zsh_dir: Path) -> str | None:
    """
    Get the installed Oh My Zsh version.

    Args:
        oh_my_zsh_dir: Directory where Oh My Zsh is installed

    Returns:
        Version string (git commit hash) if installed, None otherwise
    """
    # Oh My Zsh doesn't have a traditional version command
    # We can check the git commit hash as version
    if not check_oh_my_zsh_installed(oh_my_zsh_dir):
        return None

    try:
        # Try to get git commit hash as version
        result = subprocess.run(
            ["git", "-C", str(oh_my_zsh_dir), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        # If git fails, just return "installed"
        return "installed"

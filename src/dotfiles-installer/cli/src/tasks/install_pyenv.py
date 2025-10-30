"""Pyenv (Python Version Manager) installer utilities."""

import os
import shutil
import subprocess
from pathlib import Path


class PyenvInstallError(Exception):
    """Exception raised when pyenv installation fails."""

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


def check_pyenv_installed(pyenv_dir: Path) -> bool:
    """
    Check if pyenv is already installed.

    Args:
        pyenv_dir: Directory where pyenv should be installed

    Returns:
        True if pyenv is installed, False otherwise
    """
    # Check if pyenv binary exists in the pyenv directory
    pyenv_bin = pyenv_dir / "bin" / "pyenv"
    if not pyenv_bin.exists():
        return False

    # Try to run pyenv --version
    try:
        result = subprocess.run(
            [
                "bash",
                "-c",
                f'export PYENV_ROOT="{pyenv_dir}" && "$PYENV_ROOT/bin/pyenv" --version',
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_pyenv(
    pyenv_dir: Path,
    timeout: int = 300,
) -> None:
    """
    Install pyenv using the official installation script.

    Downloads and executes the pyenv installation script with custom directory.
    Sets PYENV_ROOT environment variable to override default installation location.
    The script installs the latest version of pyenv automatically.

    Args:
        pyenv_dir: Directory where pyenv should be installed
        timeout: Installation timeout in seconds (default: 300)

    Raises:
        PyenvInstallError: If installation fails
    """
    # Ensure parent directory exists
    pyenv_dir.parent.mkdir(parents=True, exist_ok=True)

    # Remove directory if it exists but doesn't contain a valid pyenv installation
    # This handles the case where CreateDirectoriesStep creates an empty directory
    if pyenv_dir.exists() and not check_pyenv_installed(pyenv_dir):
        try:
            shutil.rmtree(pyenv_dir)
        except OSError as e:
            raise PyenvInstallError(
                f"Failed to remove existing empty pyenv directory at {pyenv_dir}: {e}"
            ) from e

    try:
        # Download and execute the installation script with custom PYENV_ROOT
        # The pyenv-installer script respects the PYENV_ROOT environment variable
        install_url = "https://pyenv.run"

        subprocess.run(
            ["bash", "-c", f"curl -fsSL {install_url} | bash"],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
            env={
                **os.environ,
                "PYENV_ROOT": str(pyenv_dir),
            },
        )

        # Verify installation succeeded
        if not check_pyenv_installed(pyenv_dir):
            raise PyenvInstallError(
                f"Pyenv installation completed but pyenv binary not found in {pyenv_dir}. "
                "Installation may have failed."
            )

    except subprocess.TimeoutExpired as e:
        raise PyenvInstallError(
            f"Pyenv installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise PyenvInstallError(
            f"Pyenv installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e

    except FileNotFoundError as e:
        raise PyenvInstallError(
            "curl command not found. Please install curl first.",
            command="curl",
        ) from e


def get_pyenv_version(pyenv_dir: Path) -> str | None:
    """
    Get the installed pyenv version.

    Args:
        pyenv_dir: Directory where pyenv is installed

    Returns:
        Version string if installed, None otherwise
    """
    pyenv_bin = pyenv_dir / "bin" / "pyenv"
    if not pyenv_bin.exists():
        return None

    try:
        result = subprocess.run(
            [
                "bash",
                "-c",
                f'export PYENV_ROOT="{pyenv_dir}" && "$PYENV_ROOT/bin/pyenv" --version',
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        # Output format: "pyenv 2.4.17" - extract version number
        version_str: str = result.stdout.strip()
        if version_str.startswith("pyenv "):
            return version_str.split()[1]
        return version_str
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None

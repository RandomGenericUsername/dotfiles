"""Python installer utilities using pyenv."""

import os
import subprocess
from pathlib import Path


class PythonInstallError(Exception):
    """Exception raised when Python installation fails."""

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


def check_python_installed(
    pyenv_dir: Path, version: str | None = None
) -> bool:
    """
    Check if Python is installed via pyenv.

    Args:
        pyenv_dir: Directory where pyenv is installed
        version: Specific version to check (optional, checks any version if None)

    Returns:
        True if Python is installed, False otherwise
    """
    pyenv_bin = pyenv_dir / "bin" / "pyenv"
    if not pyenv_bin.exists():
        return False

    try:
        if version:
            # Check if specific version is installed
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    f'export PYENV_ROOT="{pyenv_dir}" && '
                    f'export PATH="$PYENV_ROOT/bin:$PATH" && '
                    f'eval "$(pyenv init -)" && '
                    f'pyenv versions | grep -q "{version}"',
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
                env={
                    **os.environ,
                    "PYENV_ROOT": str(pyenv_dir),
                },
            )
        else:
            # Check if any Python version is installed
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    f'export PYENV_ROOT="{pyenv_dir}" && '
                    f'export PATH="$PYENV_ROOT/bin:$PATH" && '
                    f'eval "$(pyenv init -)" && '
                    f"python --version",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
                env={
                    **os.environ,
                    "PYENV_ROOT": str(pyenv_dir),
                },
            )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_python_with_pyenv(
    pyenv_dir: Path,
    version: str,
    timeout: int = 600,
) -> None:
    """
    Install Python using pyenv.

    Args:
        pyenv_dir: Directory where pyenv is installed
        version: Python version to install (e.g., "3.12.0")
        timeout: Installation timeout in seconds (default: 600)

    Raises:
        PythonInstallError: If installation fails
    """
    pyenv_bin = pyenv_dir / "bin" / "pyenv"

    # Verify pyenv is installed
    if not pyenv_bin.exists():
        raise PythonInstallError(
            f"Pyenv not found at {pyenv_dir}. Please install pyenv first.",
            command="pyenv",
        )

    # Check if already installed
    if check_python_installed(pyenv_dir, version):
        return

    try:
        # Install Python using pyenv and set as global version
        install_cmd = (
            f'export PYENV_ROOT="{pyenv_dir}" && '
            f'export PATH="$PYENV_ROOT/bin:$PATH" && '
            f'eval "$(pyenv init -)" && '
            f"pyenv install {version} && "
            f"pyenv global {version}"
        )

        subprocess.run(
            ["bash", "-c", install_cmd],
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
        if not check_python_installed(pyenv_dir, version):
            raise PythonInstallError(
                f"Python {version} installation completed but "
                "verification failed. Python may not be properly installed."
            )

    except subprocess.TimeoutExpired as e:
        raise PythonInstallError(
            f"Python installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise PythonInstallError(
            f"Python installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e


def get_python_version(pyenv_dir: Path) -> str | None:
    """
    Get the currently active Python version.

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
                f'export PYENV_ROOT="{pyenv_dir}" && '
                f'export PATH="$PYENV_ROOT/bin:$PATH" && '
                f'eval "$(pyenv init -)" && '
                f"python --version",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
            env={
                **os.environ,
                "PYENV_ROOT": str(pyenv_dir),
            },
        )
        # Output format: "Python 3.12.0" - extract version number
        version_str: str = result.stdout.strip()
        if version_str.startswith("Python "):
            return version_str.split()[1]
        return version_str
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None

"""Pip package installer utilities for pyenv-managed Python."""

import os
import subprocess
from pathlib import Path


class PipPackageInstallError(Exception):
    """Exception raised when pip package installation fails."""

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


def check_pip_package_installed(
    pyenv_dir: Path, package: str, timeout: int = 10
) -> bool:
    """
    Check if a pip package is installed in the pyenv Python environment.

    Args:
        pyenv_dir: Directory where pyenv is installed
        package: Package name to check
        timeout: Check timeout in seconds (default: 10)

    Returns:
        True if package is installed, False otherwise
    """
    pyenv_bin = pyenv_dir / "bin" / "pyenv"
    if not pyenv_bin.exists():
        return False

    try:
        # Check if package is installed using pip show
        check_cmd = (
            f'export PYENV_ROOT="{pyenv_dir}" && '
            f'export PATH="$PYENV_ROOT/bin:$PATH" && '
            f'eval "$(pyenv init -)" && '
            f'pip show "{package}" > /dev/null 2>&1'
        )

        result = subprocess.run(
            ["bash", "-c", check_cmd],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            env={
                **os.environ,
                "PYENV_ROOT": str(pyenv_dir),
            },
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_pip_packages(
    pyenv_dir: Path,
    packages: list[str],
    upgrade: bool = False,
    timeout: int = 600,
) -> None:
    """
    Install Python packages using pip via pyenv.

    Args:
        pyenv_dir: Directory where pyenv is installed
        packages: List of package names to install
        upgrade: Whether to upgrade packages if already installed (default: False)
        timeout: Installation timeout in seconds (default: 600)

    Raises:
        PipPackageInstallError: If installation fails
    """
    if not packages:
        return

    pyenv_bin = pyenv_dir / "bin" / "pyenv"

    # Verify pyenv is installed
    if not pyenv_bin.exists():
        raise PipPackageInstallError(
            f"Pyenv not found at {pyenv_dir}. Please install pyenv first.",
            command="pyenv",
        )

    # Filter out already installed packages unless upgrade is True
    if not upgrade:
        packages_to_install = [
            pkg
            for pkg in packages
            if not check_pip_package_installed(pyenv_dir, pkg)
        ]
        if not packages_to_install:
            # All packages already installed
            return
    else:
        packages_to_install = packages

    try:
        # Install packages using pip
        upgrade_flag = "--upgrade" if upgrade else ""
        packages_str = " ".join(f'"{pkg}"' for pkg in packages_to_install)

        install_cmd = (
            f'export PYENV_ROOT="{pyenv_dir}" && '
            f'export PATH="$PYENV_ROOT/bin:$PATH" && '
            f'eval "$(pyenv init -)" && '
            f"pip install {upgrade_flag} {packages_str}"
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

        # Verify installation succeeded for each package
        failed_packages = [
            pkg
            for pkg in packages_to_install
            if not check_pip_package_installed(pyenv_dir, pkg)
        ]

        if failed_packages:
            raise PipPackageInstallError(
                f"Package installation completed but verification failed for: "
                f"{', '.join(failed_packages)}. Packages may not be properly installed."
            )

    except subprocess.TimeoutExpired as e:
        raise PipPackageInstallError(
            f"Pip package installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise PipPackageInstallError(
            f"Pip package installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e


def get_installed_pip_packages(pyenv_dir: Path) -> list[str]:
    """
    Get list of installed pip packages in the pyenv Python environment.

    Args:
        pyenv_dir: Directory where pyenv is installed

    Returns:
        List of installed package names, empty list if unable to retrieve
    """
    pyenv_bin = pyenv_dir / "bin" / "pyenv"
    if not pyenv_bin.exists():
        return []

    try:
        list_cmd = (
            f'export PYENV_ROOT="{pyenv_dir}" && '
            f'export PATH="$PYENV_ROOT/bin:$PATH" && '
            f'eval "$(pyenv init -)" && '
            f"pip list --format=freeze"
        )

        result = subprocess.run(
            ["bash", "-c", list_cmd],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
            env={
                **os.environ,
                "PYENV_ROOT": str(pyenv_dir),
            },
        )

        # Parse output: "package==version" format
        packages = []
        for line in result.stdout.strip().split("\n"):
            if line and "==" in line:
                package_name = line.split("==")[0]
                packages.append(package_name)

        return packages

    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return []

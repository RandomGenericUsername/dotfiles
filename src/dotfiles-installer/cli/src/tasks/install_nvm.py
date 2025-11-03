"""NVM (Node Version Manager) installer utilities."""

import subprocess
from pathlib import Path


class NvmInstallError(Exception):
    """Exception raised when NVM installation fails."""

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


def check_nvm_installed(nvm_dir: Path) -> bool:
    """
    Check if NVM is already installed.

    Args:
        nvm_dir: Directory where NVM should be installed

    Returns:
        True if NVM is installed, False otherwise
    """
    # Check if nvm.sh exists in the NVM directory
    nvm_script = nvm_dir / "nvm.sh"
    if not nvm_script.exists():
        return False

    # Try to source and run nvm --version
    try:
        result = subprocess.run(
            ["bash", "-c", f'source "{nvm_script}" && nvm --version'],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_nvm(
    nvm_dir: Path,
    version: str = "0.40.3",
    force: bool = False,
    timeout: int = 300,
) -> None:
    """
    Install NVM using the official installation script.

    Downloads and executes the NVM installation script with custom
    directory. Sets NVM_DIR environment variable to override default
    installation location.

    Args:
        nvm_dir: Directory where NVM should be installed
        version: NVM version to install (default: "0.40.3")
        force: Force reinstallation even if already installed
        timeout: Installation timeout in seconds (default: 300)

    Raises:
        NvmInstallError: If installation fails
    """
    # Check if already installed
    if not force and check_nvm_installed(nvm_dir):
        return

    # Ensure parent directory exists
    nvm_dir.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Download and execute the installation script with custom NVM_DIR
        install_url = f"https://raw.githubusercontent.com/nvm-sh/nvm/v{version}/install.sh"

        # Download the installation script
        curl_result = subprocess.run(
            ["curl", "-o-", install_url],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )

        # Execute the installation script with custom NVM_DIR
        # The script respects the NVM_DIR environment variable
        import os

        subprocess.run(
            ["bash"],
            input=curl_result.stdout,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
            env={
                **os.environ,
                "NVM_DIR": str(nvm_dir),
            },
        )

        # Verify installation succeeded
        if not check_nvm_installed(nvm_dir):
            raise NvmInstallError(
                f"NVM installation completed but nvm.sh not found in "
                f"{nvm_dir}. Installation may have failed."
            )

    except subprocess.TimeoutExpired as e:
        raise NvmInstallError(
            f"NVM installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise NvmInstallError(
            f"NVM installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e

    except FileNotFoundError as e:
        raise NvmInstallError(
            "curl command not found. Please install curl first.",
            command="curl",
        ) from e


def get_nvm_version(nvm_dir: Path) -> str | None:
    """
    Get the installed NVM version.

    Args:
        nvm_dir: Directory where NVM is installed

    Returns:
        Version string if installed, None otherwise
    """
    nvm_script = nvm_dir / "nvm.sh"
    if not nvm_script.exists():
        return None

    try:
        result = subprocess.run(
            ["bash", "-c", f'source "{nvm_script}" && nvm --version'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        # Output format: "0.40.3" or similar
        return result.stdout.strip()
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None

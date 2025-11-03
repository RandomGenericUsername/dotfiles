"""Node.js installer utilities using NVM."""

import subprocess
from pathlib import Path


class NodejsInstallError(Exception):
    """Exception raised when Node.js installation fails."""

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


def check_nodejs_installed(nvm_dir: Path, version: str | None = None) -> bool:
    """
    Check if Node.js is installed via NVM.

    Args:
        nvm_dir: Directory where NVM is installed
        version: Specific version to check (optional, checks any version
            if None)

    Returns:
        True if Node.js is installed, False otherwise
    """
    import os

    nvm_script = nvm_dir / "nvm.sh"
    if not nvm_script.exists():
        return False

    try:
        if version:
            # Check if specific version is installed
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    f'source "{nvm_script}" && nvm ls {version} 2>/dev/null '
                    f'| grep -q "v{version}"',
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
                env={
                    **os.environ,
                    "NVM_DIR": str(nvm_dir),
                },
            )
        else:
            # Check if any Node.js version is installed
            result = subprocess.run(
                ["bash", "-c", f'source "{nvm_script}" && node --version'],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
                env={
                    **os.environ,
                    "NVM_DIR": str(nvm_dir),
                },
            )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_nodejs_with_nvm(
    nvm_dir: Path,
    version: str,
    set_default: bool = True,
    timeout: int = 600,
) -> None:
    """
    Install Node.js using NVM.

    Args:
        nvm_dir: Directory where NVM is installed
        version: Node.js version to install (e.g., "20.9.0")
        set_default: Whether to set this version as default (default: True)
        timeout: Installation timeout in seconds (default: 600)

    Raises:
        NodejsInstallError: If installation fails
    """
    nvm_script = nvm_dir / "nvm.sh"

    # Verify NVM is installed
    if not nvm_script.exists():
        raise NodejsInstallError(
            f"NVM not found at {nvm_dir}. Please install NVM first.",
            command="nvm",
        )

    # Check if already installed
    if check_nodejs_installed(nvm_dir, version):
        return

    try:
        # Install Node.js using NVM
        import os

        install_cmd = f'source "{nvm_script}" && nvm install {version}'
        if set_default:
            install_cmd += f" && nvm alias default {version}"

        subprocess.run(
            ["bash", "-c", install_cmd],
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
        if not check_nodejs_installed(nvm_dir, version):
            raise NodejsInstallError(
                f"Node.js {version} installation completed but "
                "verification failed. Node.js may not be properly installed."
            )

    except subprocess.TimeoutExpired as e:
        raise NodejsInstallError(
            f"Node.js installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise NodejsInstallError(
            f"Node.js installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e


def get_nodejs_version(nvm_dir: Path) -> str | None:
    """
    Get the currently active Node.js version.

    Args:
        nvm_dir: Directory where NVM is installed

    Returns:
        Version string if installed, None otherwise
    """
    import os

    nvm_script = nvm_dir / "nvm.sh"
    if not nvm_script.exists():
        return None

    try:
        result = subprocess.run(
            ["bash", "-c", f'source "{nvm_script}" && node --version'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
            env={
                **os.environ,
                "NVM_DIR": str(nvm_dir),
            },
        )
        # Output format: "v20.9.0" - strip the 'v' prefix
        version_str: str = result.stdout.strip()
        return (
            version_str.lstrip("v")
            if version_str.startswith("v")
            else version_str
        )
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None

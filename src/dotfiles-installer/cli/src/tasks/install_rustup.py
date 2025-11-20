"""Rustup (Rust toolchain installer) utilities."""

import os
import subprocess
from pathlib import Path


class RustupInstallError(Exception):
    """Exception raised when Rustup installation fails."""

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


def check_rustup_installed(rustup_dir: Path, cargo_dir: Path) -> bool:
    """
    Check if Rustup is already installed.

    Args:
        rustup_dir: Directory where Rustup data is stored (RUSTUP_HOME)
        cargo_dir: Directory where Cargo/Rustup binaries are installed (CARGO_HOME)

    Returns:
        True if Rustup is installed, False otherwise
    """
    # Check if rustup binary exists in cargo bin directory
    rustup_bin = cargo_dir / "bin" / "rustup"
    if not rustup_bin.exists():
        return False

    # Try to run rustup --version
    try:
        result = subprocess.run(
            [str(rustup_bin), "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
            env={
                **os.environ,
                "RUSTUP_HOME": str(rustup_dir),
                "CARGO_HOME": str(cargo_dir),
            },
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_rustup(
    rustup_dir: Path,
    force: bool = False,
    timeout: int = 300,
) -> None:
    """
    Install Rustup using the official installation script.

    Downloads and executes the rustup-init script with custom
    directory. Sets RUSTUP_HOME and CARGO_HOME environment variables
    to override default installation location.

    Args:
        rustup_dir: Directory where Rustup should be installed
        force: Force reinstallation even if already installed
        timeout: Installation timeout in seconds (default: 300)

    Raises:
        RustupInstallError: If installation fails
    """
    # Ensure parent directory exists
    rustup_dir.parent.mkdir(parents=True, exist_ok=True)

    # Cargo will be installed alongside rustup
    cargo_dir = rustup_dir.parent / "cargo"

    # Check if already installed
    if not force and check_rustup_installed(rustup_dir, cargo_dir):
        return

    try:
        # Download the rustup-init script
        install_url = "https://sh.rustup.rs"

        curl_result = subprocess.run(
            ["curl", "--proto", "=https", "--tlsv1.2", "-sSf", install_url],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )

        # Execute the installation script with custom directories
        # -y flag makes it non-interactive
        # --no-modify-path prevents modifying shell config
        subprocess.run(
            ["sh", "-s", "--", "-y", "--no-modify-path"],
            input=curl_result.stdout,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
            env={
                **os.environ,
                "RUSTUP_HOME": str(rustup_dir),
                "CARGO_HOME": str(cargo_dir),
            },
        )

        # Verify installation succeeded
        if not check_rustup_installed(rustup_dir, cargo_dir):
            raise RustupInstallError(
                f"Rustup installation completed but rustup binary not found in "
                f"{cargo_dir}/bin. Installation may have failed."
            )

    except subprocess.TimeoutExpired as e:
        raise RustupInstallError(
            f"Rustup installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise RustupInstallError(
            f"Rustup installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e

    except FileNotFoundError as e:
        raise RustupInstallError(
            "curl command not found. Please install curl first.",
            command="curl",
        ) from e


def get_rustup_version(rustup_dir: Path, cargo_dir: Path) -> str | None:
    """
    Get the installed Rustup version.

    Args:
        rustup_dir: Directory where Rustup data is stored (RUSTUP_HOME)
        cargo_dir: Directory where Cargo/Rustup binaries are installed (CARGO_HOME)

    Returns:
        Version string if installed, None otherwise
    """
    rustup_bin = cargo_dir / "bin" / "rustup"
    if not rustup_bin.exists():
        return None

    try:
        result = subprocess.run(
            [str(rustup_bin), "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
            env={
                **os.environ,
                "RUSTUP_HOME": str(rustup_dir),
                "CARGO_HOME": str(cargo_dir),
            },
        )
        # Output format: "rustup 1.27.0 (bbb9276d2 2024-03-08)"
        # Extract just the version number
        version_line = result.stdout.strip().split("\n")[0]
        version = (
            version_line.split()[1] if len(version_line.split()) > 1 else None
        )
        return version
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None

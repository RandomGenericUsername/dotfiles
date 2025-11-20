"""Rust toolchain installer utilities using Rustup."""

import os
import subprocess
from pathlib import Path


class RustInstallError(Exception):
    """Exception raised when Rust installation fails."""

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


def check_rust_installed(
    rustup_dir: Path, cargo_dir: Path, version: str | None = None
) -> bool:
    """
    Check if Rust is installed via Rustup.

    Args:
        rustup_dir: Directory where Rustup data is stored (RUSTUP_HOME)
        cargo_dir: Directory where Cargo/Rustup binaries are installed (CARGO_HOME)
        version: Specific version to check (optional, checks any version
            if None)

    Returns:
        True if Rust is installed, False otherwise
    """
    rustup_bin = cargo_dir / "bin" / "rustup"
    cargo_bin = cargo_dir / "bin" / "cargo"

    if not rustup_bin.exists() or not cargo_bin.exists():
        return False

    try:
        if version:
            # Check if specific version is installed
            result = subprocess.run(
                [
                    str(rustup_bin),
                    "toolchain",
                    "list",
                ],
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
            # Check if version is in the output
            return (
                version in result.stdout if result.returncode == 0 else False
            )
        else:
            # Check if any Rust version is installed
            result = subprocess.run(
                [str(cargo_bin), "--version"],
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


def install_rust_with_rustup(
    rustup_dir: Path,
    cargo_dir: Path,
    version: str = "stable",
    set_default: bool = True,
    timeout: int = 600,
) -> None:
    """
    Install Rust toolchain using Rustup.

    Args:
        rustup_dir: Directory where Rustup data is stored (RUSTUP_HOME)
        cargo_dir: Directory where Cargo/Rustup binaries are installed (CARGO_HOME)
        version: Rust version to install (e.g., "1.75.0", "stable", "nightly")
        set_default: Whether to set this version as default (default: True)
        timeout: Installation timeout in seconds (default: 600)

    Raises:
        RustInstallError: If installation fails
    """
    rustup_bin = cargo_dir / "bin" / "rustup"

    # Verify Rustup is installed
    if not rustup_bin.exists():
        raise RustInstallError(
            f"Rustup not found at {cargo_dir}/bin. Please install Rustup first.",
            command="rustup",
        )

    # Check if already installed
    if check_rust_installed(rustup_dir, cargo_dir, version):
        return

    try:
        # Install Rust toolchain using Rustup
        install_cmd = [str(rustup_bin), "toolchain", "install", version]

        subprocess.run(
            install_cmd,
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

        # Set as default if requested
        if set_default:
            subprocess.run(
                [str(rustup_bin), "default", version],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
                env={
                    **os.environ,
                    "RUSTUP_HOME": str(rustup_dir),
                    "CARGO_HOME": str(cargo_dir),
                },
            )

        # Verify installation succeeded
        if not check_rust_installed(rustup_dir, cargo_dir, version):
            raise RustInstallError(
                f"Rust {version} installation completed but "
                "verification failed. Rust may not be properly installed."
            )

    except subprocess.TimeoutExpired as e:
        raise RustInstallError(
            f"Rust installation timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise RustInstallError(
            f"Rust installation failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e


def get_rust_version(rustup_dir: Path, cargo_dir: Path) -> str | None:
    """
    Get the currently active Rust version.

    Args:
        rustup_dir: Directory where Rustup data is stored (RUSTUP_HOME)
        cargo_dir: Directory where Cargo/Rustup binaries are installed (CARGO_HOME)

    Returns:
        Version string if installed, None otherwise
    """
    cargo_bin = cargo_dir / "bin" / "cargo"
    if not cargo_bin.exists():
        return None

    try:
        result = subprocess.run(
            [str(cargo_bin), "--version"],
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
        # Output format: "cargo 1.75.0 (1d8b05cdd 2023-11-20)"
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

"""Eww (ElKowar's Wacky Widgets) installer utilities."""

import os
import shutil
import subprocess
from pathlib import Path


class EwwInstallError(Exception):
    """Exception raised when Eww installation fails."""

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


def check_eww_installed(eww_bin_dir: Path) -> bool:
    """
    Check if Eww is already installed.

    Args:
        eww_bin_dir: Directory where Eww binary should be installed

    Returns:
        True if Eww is installed, False otherwise
    """
    eww_bin = eww_bin_dir / "eww"
    if not eww_bin.exists():
        return False

    try:
        result = subprocess.run(
            [str(eww_bin), "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def build_eww_from_source(
    rustup_dir: Path,
    cargo_dir: Path,
    source_dir: Path,
    install_dir: Path,
    git_url: str = "https://github.com/elkowar/eww",
    branch: str = "master",
    features: list[str] | None = None,
    force: bool = False,
    timeout: int = 600,
) -> None:
    """
    Build and install Eww from source using Cargo.

    Args:
        rustup_dir: Directory where Rustup is installed
        cargo_dir: Directory where Cargo is installed
        source_dir: Directory where to clone the Eww repository
        install_dir: Directory where to install the Eww binary
        git_url: Git repository URL (default: official Eww repo)
        branch: Git branch to checkout (default: "master")
        features: List of features to enable (e.g., ["wayland", "x11"])
        force: Force rebuild even if already installed
        timeout: Build timeout in seconds (default: 600)

    Raises:
        EwwInstallError: If build or installation fails
    """
    if features is None:
        features = ["wayland", "x11"]

    eww_bin_dir = install_dir / "bin"
    eww_bin = eww_bin_dir / "eww"

    # Check if already installed
    if not force and check_eww_installed(eww_bin_dir):
        return

    # Verify Cargo is installed
    cargo_bin = cargo_dir / "bin" / "cargo"
    if not cargo_bin.exists():
        raise EwwInstallError(
            f"Cargo not found at {cargo_dir}. Please install Rust first.",
            command="cargo",
        )

    # Ensure directories exist
    source_dir.parent.mkdir(parents=True, exist_ok=True)
    eww_bin_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Clone or update repository
        is_git_repo = (
            (source_dir / ".git").exists() if source_dir.exists() else False
        )

        if source_dir.exists() and is_git_repo:
            # Update existing repository
            subprocess.run(
                ["git", "-C", str(source_dir), "fetch", "origin"],
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
            subprocess.run(
                ["git", "-C", str(source_dir), "checkout", branch],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            subprocess.run(
                ["git", "-C", str(source_dir), "pull", "origin", branch],
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
        else:
            # Remove non-git directory if it exists
            if source_dir.exists():
                shutil.rmtree(source_dir)

            # Clone repository
            subprocess.run(
                ["git", "clone", "--branch", branch, git_url, str(source_dir)],
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )

        # Build with Cargo
        features_str = ",".join(features)
        build_cmd = [
            str(cargo_bin),
            "build",
            "--release",
            "--no-default-features",
            "--features",
            features_str,
        ]

        subprocess.run(
            build_cmd,
            cwd=source_dir,
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

        # Copy binary to install directory
        built_binary = source_dir / "target" / "release" / "eww"
        if not built_binary.exists():
            raise EwwInstallError(
                f"Build completed but binary not found at {built_binary}. "
                "Build may have failed."
            )

        shutil.copy2(built_binary, eww_bin)
        eww_bin.chmod(0o755)

        # Verify installation succeeded
        if not check_eww_installed(eww_bin_dir):
            raise EwwInstallError(
                f"Eww installation completed but eww binary not found in "
                f"{eww_bin_dir}. Installation may have failed."
            )

    except subprocess.TimeoutExpired as e:
        raise EwwInstallError(
            f"Eww build timed out after {timeout}s",
            command=str(e.cmd) if hasattr(e, "cmd") else None,
        ) from e

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise EwwInstallError(
            f"Eww build failed: {error_msg}",
            command=" ".join(e.cmd) if e.cmd else None,
            exit_code=e.returncode,
        ) from e

    except FileNotFoundError as e:
        raise EwwInstallError(
            f"Required command not found: {e}",
            command=str(e),
        ) from e


def get_eww_version(eww_bin_dir: Path) -> str | None:
    """
    Get the installed Eww version.

    Args:
        eww_bin_dir: Directory where Eww binary is installed

    Returns:
        Version string if installed, None otherwise
    """
    eww_bin = eww_bin_dir / "eww"
    if not eww_bin.exists():
        return None

    try:
        result = subprocess.run(
            [str(eww_bin), "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        # Output format: "eww 0.4.0" or similar
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

"""Project root path management.

This module provides the project root path that is set once at application
startup (in main.py) and made available throughout the application.

This approach is similar to setting a variable in bash at the start of a script
and using it throughout - simple, explicit, and reliable.

Usage:
    # In main.py (entry point):
    from src.config.project_root import set_project_root
    from pathlib import Path

    # Set it once at startup - use Path(__file__).parent to go up from main.py
    # main.py is at: src/dotfiles-installer/cli/main.py
    # So we need to go up 4 levels to reach project root
    set_project_root(Path(__file__).parent.parent.parent.parent)

    # In any other module:
    from src.config.project_root import get_project_root, get_project_path

    root = get_project_root()
    config_path = root / "settings.toml"
    templates = get_project_path("src/dotfiles-installer/docker/templates")
"""

from pathlib import Path

# Global project root - set once at application startup
# Initially None, must be set by calling set_project_root() before use
_PROJECT_ROOT: Path | None = None


def set_project_root(root: Path) -> None:
    """Set the project root path.

    This should be called ONCE at application startup (in main.py).

    Args:
        root: Absolute path to the project root directory

    Raises:
        ValueError: If root doesn't exist or isn't a directory
        RuntimeError: If project root has already been set

    Example:
        >>> from pathlib import Path
        >>> set_project_root(Path("/home/user/Development/new"))
    """
    global _PROJECT_ROOT

    if _PROJECT_ROOT is not None:
        raise RuntimeError(
            f"Project root already set to {_PROJECT_ROOT}. "
            "It should only be set once at application startup."
        )

    root = root.resolve()  # Convert to absolute path

    if not root.exists():
        raise ValueError(f"Project root does not exist: {root}")

    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")

    _PROJECT_ROOT = root


def get_project_root() -> Path:
    """Get the project root path.

    Returns:
        Absolute path to project root

    Raises:
        RuntimeError: If project root has not been set yet

    Example:
        >>> root = get_project_root()
        >>> print(root)
        /home/user/Development/new
    """
    if _PROJECT_ROOT is None:
        raise RuntimeError(
            "Project root not set. Call set_project_root() in main.py first."
        )
    return _PROJECT_ROOT


def get_project_path(*path_parts: str) -> Path:
    """Get a path relative to the project root.

    This is a convenience function that joins path parts relative to
    the project root.

    Args:
        *path_parts: Path components to join relative to project root

    Returns:
        Absolute path relative to project root

    Raises:
        RuntimeError: If project root has not been set yet

    Examples:
        >>> get_project_path('src', 'dotfiles-installer', 'cli')
        /home/user/Development/new/src/dotfiles-installer/cli

        >>> get_project_path('settings.toml')
        /home/user/Development/new/settings.toml
    """
    return get_project_root().joinpath(*path_parts)

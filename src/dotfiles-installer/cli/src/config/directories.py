import re
from pathlib import Path

import tomli

from src.config.project_root import get_project_root

# ============================================================================
# Path Resolution with Template Variables
# ============================================================================


def load_paths_from_toml(
    section: str, base_path: Path, toml_file: Path | None = None
) -> dict[str, Path]:
    """Load paths from TOML file with template variable resolution.

    Template variables use {variable_name} syntax and are resolved iteratively.
    Variables can reference other variables in the same section.

    Args:
        section: TOML section to load (e.g., "install", "source", "host")
        base_path: Base directory to prepend to all paths
        toml_file: Path to TOML file (defaults to config/directories.toml)

    Returns:
        Dictionary mapping semantic path names to resolved Path objects

    Example:
        >>> paths = load_paths_from_toml("install", Path("/home/user"))
        >>> paths["dotfiles"]
        PosixPath('/home/user/dotfiles')
        >>> paths["dotfiles_starship"]  # Resolved from {dotfiles}/starship
        PosixPath('/home/user/dotfiles/starship')
    """
    if toml_file is None:
        # TOML file is in cli/config/, this file is in cli/src/config/
        toml_file = (
            Path(__file__).parent.parent.parent / "config" / "directories.toml"
        )

    # Load TOML file
    with toml_file.open("rb") as f:
        config = tomli.load(f)

    if section not in config:
        raise ValueError(f"Section '{section}' not found in {toml_file}")

    raw_paths = config[section]
    resolved_paths: dict[str, str] = {}

    # Iteratively resolve template variables
    max_iterations = 100  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        changed = False

        for key, value in raw_paths.items():
            if key in resolved_paths:
                continue  # Already fully resolved

            # Try to resolve template variables in this value
            resolved_value = value
            template_pattern = re.compile(r"\{([^}]+)\}")

            # Find all template variables
            matches = template_pattern.findall(value)

            if not matches:
                # No template variables, mark as resolved
                resolved_paths[key] = value
                changed = True
                continue

            # Try to substitute all template variables
            all_resolved = True
            for var_name in matches:
                if var_name in resolved_paths:
                    # Replace {var_name} with its resolved value
                    resolved_value = resolved_value.replace(
                        f"{{{var_name}}}", resolved_paths[var_name]
                    )
                else:
                    # Variable not yet resolved
                    all_resolved = False
                    break

            if all_resolved:
                resolved_paths[key] = resolved_value
                changed = True

        # Check if all paths are resolved
        if len(resolved_paths) == len(raw_paths):
            break

        # If nothing changed in this iteration, we have unresolvable variables
        if not changed:
            unresolved = set(raw_paths.keys()) - set(resolved_paths.keys())
            raise ValueError(
                f"Unable to resolve template variables in paths: {unresolved}"
            )

    # Convert to Path objects with base_path prepended
    result = {key: base_path / value for key, value in resolved_paths.items()}

    # Add special _root key for the base path
    result["_root"] = base_path

    return result


# ============================================================================
# Host Paths (User's system directories)
# ============================================================================

HOST_ROOT = Path.home()


def load_host_paths(root: Path | None = None) -> dict[str, Path]:
    """Load host system paths from TOML configuration.

    Args:
        root: Root directory for host paths (defaults to Path.home())

    Returns:
        Dictionary mapping semantic path names to Path objects
    """
    if root is None:
        root = HOST_ROOT
    return load_paths_from_toml("host", root)


# ============================================================================
# Installation Paths (Where dotfiles will be installed on user's system)
# ============================================================================


def load_install_paths(root: Path) -> dict[str, Path]:
    """Load installation paths from TOML configuration.

    This is the SINGLE SOURCE OF TRUTH for installation directory structure.
    Path definitions are in config/directories.toml.

    Args:
        root: Root directory for installation paths

    Returns:
        Dictionary mapping semantic path names to Path objects
    """
    return load_paths_from_toml("install", root)


# ============================================================================
# Source Paths (Project source files)
# ============================================================================

SRC_ROOT = get_project_root() / "src"


def load_source_paths(root: Path | None = None) -> dict[str, Path]:
    """Load source paths from TOML configuration.

    This is the SINGLE SOURCE OF TRUTH for source directory structure.
    Path definitions are in config/directories.toml.

    Args:
        root: Root directory for source paths (defaults to project_root/src)

    Returns:
        Dictionary mapping semantic path names to Path objects
    """
    if root is None:
        root = SRC_ROOT
    return load_paths_from_toml("source", root)

from pathlib import Path

from dotfiles_package_manager import PackageManagerFactory, PackageManagerType
from filesystem_path_builder import PathsBuilder
from src.config.project_root import get_project_root

# ============================================================================
# Distribution-Specific Package Configuration Helper
# ============================================================================


def get_distro_packages_path() -> Path:
    """
    Detect package manager and return path to distro-specific system.toml.

    This function auto-detects the system's package manager and maps it to
    the appropriate distribution configuration directory.

    Returns:
        Path to the appropriate system.toml file based on detected
        package manager

    Raises:
        FileNotFoundError: If distro config file doesn't exist

    Example:
        >>> path = get_distro_packages_path()
        >>> # On Arch with paru: .../config/packages/arch/system.toml
        >>> # On Debian with apt: .../config/packages/debian/system.toml
    """
    # Map package manager type to distribution directory
    distro_map = {
        # Arch Linux family
        PackageManagerType.PACMAN: "arch",
        PackageManagerType.YAY: "arch",
        PackageManagerType.PARU: "arch",
        # Debian/Ubuntu family
        PackageManagerType.APT: "debian",
        PackageManagerType.APT_GET: "debian",
        # RedHat/Fedora family
        PackageManagerType.DNF: "redhat",
        PackageManagerType.YUM: "redhat",
    }

    try:
        # Auto-detect package manager
        pm = PackageManagerFactory.create_auto(prefer_third_party=True)
        distro = distro_map.get(pm.manager_type, "arch")
    except Exception:
        # Fallback to arch if detection fails
        distro = "arch"

    # Construct path to distro-specific config
    # Use get_project_root() which is set in main.py at application startup
    project_root = get_project_root()
    packages_dir = (
        project_root
        / "src"
        / "dotfiles-installer"
        / "cli"
        / "config"
        / "packages"
    )
    distro_config_path: Path = packages_dir / distro / "system.toml"

    if not distro_config_path.exists():
        raise FileNotFoundError(
            f"Distribution config not found: {distro_config_path}"
        )

    return distro_config_path


# ============================================================================
# Host Paths (User's system directories)
# ============================================================================

HOST_ROOT = Path.home()
_host_builder = PathsBuilder(HOST_ROOT)
_host_builder.add_path("cache", hidden=True)
host_builder = _host_builder
host = _host_builder.build()


# ============================================================================
# Installation Paths (Where dotfiles will be installed on user's system)
# ============================================================================

# NOTE: This is a PLACEHOLDER that is ALWAYS replaced by
# AppConfig.model_post_init()
# The actual installation root comes from:
#   1. CLI arguments (--install-dir)
#   2. User settings.toml (installation_directory)
#   3. Project defaults.toml (installation_directory)
# This placeholder exists only to satisfy initial imports before
# AppConfig is created.
# DO NOT rely on this value - it will be replaced!

_PLACEHOLDER_INSTALL_ROOT = Path.home() / ".tmp" / "dotfiles-placeholder"


# ======================== Base directory ================================= #

# Placeholder builder - WILL BE REPLACED by AppConfig.model_post_init()
_install_builder = PathsBuilder(_PLACEHOLDER_INSTALL_ROOT)


# =====================First level directories ======================== #

# Directory for dotfiles (symlinks to original files)
_install_builder.add_path("dotfiles")
# Directory for dependencies files
_install_builder.add_path("dependencies", hidden=True)
# Directory for scripts
_install_builder.add_path("scripts")


# =====================Second level directories ======================= #
# ----------------------------- Dotfiles ------------------------------ #
_install_builder.add_path("dotfiles.starship")
_install_builder.add_path("dotfiles.zsh", hidden=True)

# ----------------------------- Dependencies ------------------------------ #
_install_builder.add_path("dependencies.nvm")
_install_builder.add_path("dependencies.pyenv")
_install_builder.add_path("dependencies.oh-my-zsh")
# ----------------------------- config ------------------------------ #
_install_builder.add_path("dotfiles.config")
# ----------------------------- scripts ----------------------------- #


# Export the builder so AppConfig.model_post_init() can copy path definitions
# This is the SINGLE SOURCE OF TRUTH for installation directory structure
install_builder = _install_builder

# Export ManagedPathTree (combines navigation and create())
# WARNING: This is a PLACEHOLDER and will be replaced by
# AppConfig.model_post_init()
# Always access via: app_config.project.paths.install
# The install object provides:
#   - install.create() - Create all registered directories
#   - install.path - Get root installation path
#   - install.dotfiles.starship.path - Navigate to any registered path
#   - install.dotfiles.starship.file('x') - Get file paths
install = _install_builder.build()


# ============================================================================
# Source Paths (Project source files)
# ============================================================================

# Uncomment when needed:
# source = PathTree.from_str(get_project_root() / "src")


# ============================================================================
# Runtime Paths (Logs, cache, temporary files)
# ============================================================================

# Uncomment when needed:
# runtime = PathTree.from_str(Path.home() / ".local/share/dotfiles")

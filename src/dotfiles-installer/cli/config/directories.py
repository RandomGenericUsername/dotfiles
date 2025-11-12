from pathlib import Path

from filesystem_path_builder import PathsBuilder

from src.config.project_root import get_project_root

# ============================================================================
# Host Paths (User's system directories)
# ============================================================================

HOST_ROOT = Path.home()


def create_host_builder(root: Path, strict: bool = False) -> PathsBuilder:
    """Create a PathsBuilder with all host system directories.

    This is the SINGLE SOURCE OF TRUTH for host directory structure.

    Args:
        root: Root directory for host paths (typically Path.home())
        strict: If True, only registered paths can be accessed (catches typos)

    Returns:
        PathsBuilder configured with all host subdirectories
    """
    builder = PathsBuilder(root, strict=strict)

    # Hidden cache directory
    builder.add_path("cache", hidden=True)

    return builder


# ============================================================================
# Installation Paths (Where dotfiles will be installed on user's system)
# ============================================================================


def create_install_builder(root: Path, strict: bool = True) -> PathsBuilder:
    """Create a PathsBuilder with all installation subdirectories.

    This is the SINGLE SOURCE OF TRUTH for installation directory structure.

    Args:
        root: Root directory for installation paths
        strict: If True, only registered paths can be accessed (catches typos)

    Returns:
        PathsBuilder configured with all installation subdirectories
    """
    builder = PathsBuilder(root, strict=strict)

    # =====================First level directories ======================== #

    # Directory for dotfiles (symlinks to original files)
    builder.add_path("dotfiles")
    # Directory for dependencies files
    builder.add_path("dependencies", hidden=True)
    # Directory for scripts
    builder.add_path("modules")
    # Directory for tools
    builder.add_path("tools")

    # =====================Second level directories ======================= #
    # ----------------------------- Dotfiles ------------------------------ #
    builder.add_path("dotfiles.starship")
    builder.add_path("dotfiles.zsh")
    builder.add_path("dotfiles.wallpapers")
    builder.add_path("dotfiles.wlogout")
    builder.add_path("dotfiles.cache", hidden=True)

    # ----------------------------- Dependencies -------------------------- #
    builder.add_path("dependencies.nvm")
    builder.add_path("dependencies.pyenv")
    builder.add_path("dependencies.oh-my-zsh")
    builder.add_path("dependencies.modules")
    builder.add_path("dependencies.tools")
    # ----------------------------- config -------------------------------- #
    builder.add_path("dotfiles.config")
    builder.add_path("dotfiles.config.hypr")
    # ----------------------------- scripts ------------------------------- #

    builder.add_path("dependencies.modules.logging")
    builder.add_path("dependencies.modules.pipeline")
    builder.add_path("dependencies.modules.package-manager")
    builder.add_path("dependencies.modules.container-manager")
    builder.add_path("dependencies.modules.colorscheme-generator")
    builder.add_path("dependencies.modules.wallpaper-effects-processor")
    builder.add_path("dependencies.modules.state-manager")
    builder.add_path("dependencies.modules.hyprpaper-manager")

    builder.add_path("dependencies.tools.colorscheme-orchestrator")
    builder.add_path("dependencies.tools.wallpaper-effects-orchestrator")
    builder.add_path("dependencies.tools.wallpaper-orchestrator")

    builder.add_path("dotfiles.wlogout.templates")
    builder.add_path("dotfiles.wlogout.templates.icons")

    return builder


# ============================================================================
# Source Paths (Project source files)
# ============================================================================

SRC_ROOT = get_project_root() / "src"


def create_src_builder(root: Path, strict: bool = False) -> PathsBuilder:
    """Create a PathsBuilder with all project source directories.

    This is the SINGLE SOURCE OF TRUTH for source directory structure.

    Args:
        root: Root directory for source paths (typically project_root/src)
        strict: If True, only registered paths can be accessed (catches typos)

    Returns:
        PathsBuilder configured with all source subdirectories
    """
    builder = PathsBuilder(root, strict=strict)

    # =====================First level directories ======================== #
    builder.add_path("common")
    builder.add_path("dotfiles")
    builder.add_path("dotfiles-installer")

    # =====================Second level directories ======================= #
    builder.add_path("common.modules")
    builder.add_path("common.tools")

    builder.add_path("dotfiles.assets")
    builder.add_path("dotfiles.config-files")
    builder.add_path("dotfiles.modules")
    builder.add_path("dotfiles.scripts")

    # =====================Third level directories ======================== #
    builder.add_path("dotfiles.assets.wallpapers")

    return builder

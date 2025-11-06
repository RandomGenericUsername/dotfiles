from pathlib import Path

from filesystem_path_builder import PathsBuilder

from src.config.project_root import get_project_root

# ============================================================================
# Host Paths (User's system directories)
# ============================================================================

HOST_ROOT = Path.home()
_host_builder = PathsBuilder(HOST_ROOT)
_host_builder.add_path("cache", hidden=True)
_host_builder.add_path("Wallpapers")
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
_install_builder.add_path("dotfiles.zsh")
_install_builder.add_path("dotfiles.wallpapers")

# ----------------------------- Dependencies ------------------------------ #
_install_builder.add_path("dependencies.nvm")
_install_builder.add_path("dependencies.pyenv")
_install_builder.add_path("dependencies.oh-my-zsh")
# ----------------------------- config ------------------------------ #
_install_builder.add_path("dotfiles.config")
_install_builder.add_path("dotfiles.config.hypr")
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

#
SRC_ROOT = get_project_root() / "src"
src_builder = PathsBuilder(SRC_ROOT)

src_builder.add_path("common")
src_builder.add_path("dotfiles")
src_builder.add_path("dotfiles-installer")

src_builder.add_path("common.modules")
src_builder.add_path("common.tools")

src_builder.add_path("dotfiles.assets")
src_builder.add_path("dotfiles.config-files")
src_builder.add_path("dotfiles.modules")
src_builder.add_path("dotfiles.scripts")

src_builder.add_path("dotfiles.assets.wallpapers")

src = src_builder.build()

# Proposed PathsConfig Implementation

This document provides concrete implementation examples for the proposed unified path configuration system.

## 1. Project Root Detection

### File: `cli/src/config/project_root.py` (NEW)

```python
"""Robust project root detection using marker files."""

from pathlib import Path


def find_project_root(
    start_path: Path | None = None,
    marker_files: list[str] | None = None,
) -> Path:
    """Find project root by looking for marker files.
    
    This function searches upward from the starting path (or current file)
    looking for files that indicate the project root. This is more robust
    than using a fixed number of .parent calls.
    
    Args:
        start_path: Path to start searching from. Defaults to this file's location.
        marker_files: Files that indicate project root.
                     Defaults to ['pyproject.toml', '.git', 'settings.toml']
    
    Returns:
        Path to project root (absolute path)
        
    Raises:
        RuntimeError: If project root cannot be found
        
    Examples:
        >>> root = find_project_root()
        >>> print(root)
        /home/user/Development/new
        
        >>> # Custom markers
        >>> root = find_project_root(marker_files=['setup.py', '.git'])
    """
    if marker_files is None:
        marker_files = ['pyproject.toml', '.git', 'settings.toml']
    
    if start_path is None:
        start_path = Path(__file__).resolve()
    else:
        start_path = start_path.resolve()
    
    # Search upward through parent directories
    for parent in [start_path] + list(start_path.parents):
        if any((parent / marker).exists() for marker in marker_files):
            return parent
    
    # If we get here, we couldn't find the project root
    raise RuntimeError(
        f"Could not find project root starting from {start_path}. "
        f"Looked for marker files: {', '.join(marker_files)}"
    )


# Global project root - computed once on import
PROJECT_ROOT = find_project_root()
```

## 2. Unified PathsConfig Models

### File: `cli/src/config/config.py` (UPDATED)

```python
"""Configuration models with unified path management."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from src.config.project_root import PROJECT_ROOT


class ProjectPaths(BaseModel):
    """Paths within the project repository.
    
    These paths are relative to the auto-detected project root and point
    to directories within the repository itself. They are typically not
    user-configurable as they define the project structure.
    
    All relative paths are resolved relative to the project root.
    """
    
    root: Path = Field(
        default=PROJECT_ROOT,
        description="Project root directory (auto-detected)"
    )
    
    templates: Path = Field(
        default=Path("src/dotfiles-installer/docker/templates"),
        description="Docker templates directory (relative to root)"
    )
    
    docker: Path = Field(
        default=Path("src/dotfiles-installer/docker"),
        description="Docker configuration directory (relative to root)"
    )
    
    cli_config: Path = Field(
        default=Path("src/dotfiles-installer/cli/config"),
        description="CLI configuration directory (relative to root)"
    )
    
    @model_validator(mode='after')
    def resolve_relative_paths(self) -> 'ProjectPaths':
        """Resolve all relative paths relative to project root."""
        for field_name in ['templates', 'docker', 'cli_config']:
            path = getattr(self, field_name)
            if not path.is_absolute():
                setattr(self, field_name, self.root / path)
        return self


class InstallationPaths(BaseModel):
    """Paths for dotfiles installation.
    
    These paths define where dotfiles will be installed on the user's system.
    They are user-configurable and typically point to locations in the user's
    home directory or other user-specified locations.
    """
    
    directory: Path = Field(
        description="Main installation directory"
    )
    
    backup: Path = Field(
        description="Backup directory for existing dotfiles"
    )
    
    # Dynamic subdirectories (from directories.toml)
    # This will be populated by InstallationPaths class (existing implementation)
    subdirs: 'DynamicInstallationPaths | None' = Field(
        default=None,
        description="Dynamic subdirectories structure"
    )


class DynamicInstallationPaths(BaseModel):
    """Dynamic installation subdirectories.
    
    This is the existing InstallationPaths implementation that provides
    dynamic attribute access to subdirectories defined in directories.toml.
    
    Renamed to avoid confusion with the new InstallationPaths.
    """
    # ... existing InstallationPaths implementation ...
    pass


class HostPaths(BaseModel):
    """Paths on the host system.
    
    These paths point to user directories on the host system that are
    used by the dotfiles (e.g., wallpapers, screenshots). They are
    user-configurable.
    """
    
    wallpapers: Path = Field(
        description="Wallpapers directory"
    )
    
    screenshots: Path = Field(
        description="Screenshots directory"
    )


class RuntimePaths(BaseModel):
    """Runtime paths for logs, cache, etc.
    
    These paths are used by the application at runtime for temporary
    storage, logs, and cache. They are user-configurable.
    """
    
    logs: Path = Field(
        description="Log files directory"
    )
    
    cache: Path = Field(
        description="Cache directory"
    )


class PathsConfig(BaseModel):
    """Unified path configuration - single source of truth for all paths.
    
    This model consolidates all path configuration into a single, well-organized
    structure. Instead of paths being scattered across multiple models, they are
    all accessible through config.paths.*.
    
    Path Categories:
    - project: Paths within the project repository (auto-detected root)
    - installation: Paths for dotfiles installation (user-configurable)
    - host: Paths on the host system (user-configurable)
    - runtime: Paths for logs, cache, etc. (user-configurable)
    
    Examples:
        >>> config = AppConfig()
        >>> print(config.paths.project.root)
        /home/user/Development/new
        
        >>> print(config.paths.project.templates)
        /home/user/Development/new/src/dotfiles-installer/docker/templates
        
        >>> print(config.paths.installation.directory)
        /home/user/dotfiles
        
        >>> print(config.paths.host.wallpapers)
        /home/user/wallpapers
        
        >>> print(config.paths.runtime.logs)
        /home/user/.local/share/dotfiles/logs
    """
    
    project: ProjectPaths = Field(
        default_factory=ProjectPaths,
        description="Project repository paths (auto-detected)"
    )
    
    installation: InstallationPaths = Field(
        description="Dotfiles installation paths (user-configurable)"
    )
    
    host: HostPaths = Field(
        description="Host system paths (user-configurable)"
    )
    
    runtime: RuntimePaths = Field(
        description="Runtime paths for logs, cache, etc. (user-configurable)"
    )


class InstallSettings(BaseModel):
    """Installation behavior settings.
    
    NOTE: Paths have been moved to PathsConfig.
    This model now only contains installation behavior settings.
    """
    
    type: InstallType = Field(
        default=InstallType.update,
        description="Type of installation (update or clean)"
    )
    
    hidden: bool = Field(
        default=True,
        description="Hide the install directory (prefix with dot)"
    )
    
    debug: InstallDebugSettings = Field(
        default_factory=InstallDebugSettings,
        description="Debug and logging settings"
    )


class InstallDebugSettings(BaseModel):
    """Debug and logging settings.
    
    NOTE: log_directory has been moved to PathsConfig.runtime.logs
    """
    
    log_level: LogLevels = Field(
        description="Log level"
    )
    
    output_to_file: bool = Field(
        description="Output log to file"
    )


class AppConfig(BaseModel):
    """Application configuration with unified path management.
    
    This is the root configuration model. The key change is that ALL paths
    are now consolidated under the 'paths' attribute, making them easy to
    find and manage.
    """
    
    # ALL PATHS IN ONE PLACE
    paths: PathsConfig = Field(
        description="All path configuration (unified)"
    )
    
    # Installation settings (behavior only, no paths)
    install: InstallSettings = Field(
        default_factory=InstallSettings,
        description="Installation behavior settings"
    )
    
    # System configuration
    system: SystemConfig = Field(
        default_factory=SystemConfig,
        description="System packages and features"
    )
    
    # Tool configurations
    package_manager: PackageManagerSettings = Field(
        default_factory=PackageManagerSettings,
        description="Package manager settings"
    )
    
    container_manager: ContainerManagerSettings = Field(
        default_factory=ContainerManagerSettings,
        description="Container manager settings"
    )
    
    template_renderer: TemplateRendererSettings = Field(
        default_factory=TemplateRendererSettings,
        description="Template renderer settings"
    )
    
    # Safety settings
    safety: SafetySettings = Field(
        default_factory=SafetySettings,
        description="Safety settings"
    )
```

## 3. Configuration TOML Files

### File: `cli/config/defaults.toml` (NEW)

```toml
# ============================================================================
# Default Configuration Values
# ============================================================================
# This file contains ALL default values for the dotfiles installer.
# User overrides should go in the root settings.toml file.
#
# Configuration Hierarchy:
# 1. This file (defaults.toml) - Project defaults
# 2. directories.toml - Directory structure
# 3. settings.toml (in cli/config) - Project settings
# 4. settings.toml (in project root) - User overrides (highest priority)
# ============================================================================

# ============================================================================
# Path Configuration
# ============================================================================

[paths.project]
# Project paths are relative to auto-detected project root
# The root itself is auto-detected using marker files (pyproject.toml, .git, etc.)
templates = "src/dotfiles-installer/docker/templates"
docker = "src/dotfiles-installer/docker"
cli_config = "src/dotfiles-installer/cli/config"

[paths.installation]
# Installation paths are user-configurable
# Environment variables like $HOME are automatically expanded
directory = "$HOME/dotfiles"
backup = "$HOME/.dotfiles-backup"

[paths.host]
# Host system paths
wallpapers = "$HOME/wallpapers"
screenshots = "$HOME/Pictures/Screenshots"

[paths.runtime]
# Runtime paths for logs, cache, etc.
logs = "$HOME/.local/share/dotfiles/logs"
cache = "$HOME/.cache/dotfiles"

# ============================================================================
# Installation Settings
# ============================================================================

[install]
type = "update"  # Options: "update" or "clean"
hidden = true    # Prefix install directory with dot

[install.debug]
log_level = "error"      # Options: "debug", "info", "warning", "error"
output_to_file = false   # Write logs to file

# ============================================================================
# Package Manager Settings
# ============================================================================

[package_manager]
prefer_third_party = true              # Prefer paru/yay on Arch for AUR access
update_system_before_install = false   # Update system before installing packages
remove_dependencies = true             # Remove unused dependencies when uninstalling

# ============================================================================
# Container Manager Settings
# ============================================================================

[container_manager]
runtime = "docker"           # Options: "docker" or "podman"
build_timeout = 600          # Build timeout in seconds
default_registry = "docker.io"
cache_enabled = true

# ============================================================================
# Template Renderer Settings
# ============================================================================

[template_renderer]
# NOTE: template_directory is now in paths.project.templates
default_template = "python.j2"
strict_mode = true  # Fail on missing template variables

# ============================================================================
# Safety Settings
# ============================================================================

[safety.directory_deletion]
# Protected directories that should never be deleted
protected_directories = [
  # System root and core directories
  "/", "/root", "/usr", "/etc", "/var", "/bin", "/sbin", "/lib", "/boot",
  "/sys", "/proc", "/dev",
  # User and home directories
  "/home", "/Users",
  # Mount points and external storage
  "/mnt", "/media", "/run/media",
  # Package managers and applications
  "/opt", "/usr/local", "/snap", "/opt/homebrew", "/flatpak",
  # Service and application data
  "/var/www", "/srv", "/var/lib", "/var/log", "/var/spool",
  # Common backup and temp locations
  "/backup", "/backups", "/tmp", "/var/tmp",
]

# Keywords that make a path dangerous to delete
dangerous_keywords = ["system", "root", "backup", "config"]

# Minimum path depth required (number of path segments)
minimum_path_depth = 3

# Whether to protect direct user home directories (/home/username)
protect_user_homes = true

# Minimum depth for keyword checking (keywords only checked for shallow paths)
keyword_check_depth_threshold = 4
```

### File: `settings.toml` (ROOT - User Overrides)

```toml
# ============================================================================
# User Configuration Overrides
# ============================================================================
# This file contains user-specific overrides for the dotfiles installer.
# Only include settings you want to override from the defaults.
# ============================================================================

# Override installation paths
[paths.installation]
directory = "$HOME/.tmp/install"
backup = "$HOME/.tmp/backup"

# Override runtime paths
[paths.runtime]
logs = "/tmp/dotfiles/logs"

# Override host paths
[paths.host]
wallpapers = "$HOME/wallpapers"
screenshots = "$HOME/Pictures/Screenshots"

# Override installation settings
[install]
type = "update"
hidden = true

[install.debug]
log_level = "info"
output_to_file = true
```

## 4. Updated Settings Loader

### File: `cli/src/config/settings.py` (UPDATED)

```python
"""Settings loader with robust project root detection."""

import os
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf
from pydantic import ValidationError

from src.config.config import AppConfig as PydanticAppConfig
from src.config.project_root import PROJECT_ROOT

# Configuration files in loading order (later files override earlier ones)
DEFAULTS_CONFIG = PROJECT_ROOT / "src/dotfiles-installer/cli/config/defaults.toml"
DIRECTORIES_CONFIG = PROJECT_ROOT / "src/dotfiles-installer/cli/config/directories.toml"
PROJECT_SETTINGS = PROJECT_ROOT / "src/dotfiles-installer/cli/config/settings.toml"
USER_SETTINGS = PROJECT_ROOT / "settings.toml"

# Clear, documented loading order
settings_files = [
    str(DEFAULTS_CONFIG),      # 1. Project defaults (NEW)
    str(DIRECTORIES_CONFIG),   # 2. Directory structure
    str(PROJECT_SETTINGS),     # 3. Project settings
    str(USER_SETTINGS),        # 4. User overrides (highest priority)
]


class SettingsModel:
    """Settings loader using dynaconf + Pydantic."""
    
    def __init__(self, settings_files: list[str], project_root: Path = PROJECT_ROOT):
        self.project_root = project_root
        
        # Load settings with dynaconf
        self.dynaconf_settings: Dynaconf = Dynaconf(
            settings_files=settings_files,
        )
        
        # Convert and validate
        settings_dict = self._convert_dict_to_lower_case(
            self._resolve_environment_variables(
                self.dynaconf_settings.to_dict()
            )
        )
        
        # Inject project root for path resolution
        if 'paths' not in settings_dict:
            settings_dict['paths'] = {}
        if 'project' not in settings_dict['paths']:
            settings_dict['paths']['project'] = {}
        settings_dict['paths']['project']['root'] = project_root
        
        # Validate with Pydantic
        self.settings: PydanticAppConfig = self.get_pydantic_config(settings_dict)
    
    # ... rest of the implementation ...


# Global settings instance
Settings: SettingsModel = SettingsModel(settings_files=settings_files)
```

## 5. Usage Examples

### Accessing Paths

```python
from src.config.settings import Settings

config = Settings.get()

# Project paths (auto-detected)
print(config.paths.project.root)       # /home/user/Development/new
print(config.paths.project.templates)  # /home/user/Development/new/src/.../templates
print(config.paths.project.docker)     # /home/user/Development/new/src/.../docker

# Installation paths (user-configurable)
print(config.paths.installation.directory)  # /home/user/dotfiles
print(config.paths.installation.backup)     # /home/user/.dotfiles-backup

# Host paths (user-configurable)
print(config.paths.host.wallpapers)     # /home/user/wallpapers
print(config.paths.host.screenshots)    # /home/user/Pictures/Screenshots

# Runtime paths (user-configurable)
print(config.paths.runtime.logs)   # /home/user/.local/share/dotfiles/logs
print(config.paths.runtime.cache)  # /home/user/.cache/dotfiles
```

### Migration from Old to New

```python
# OLD (scattered):
install_dir = config.install.directory
log_dir = config.install.debug.log_directory
wallpapers = config.host_paths.wallpapers_directory
templates = config.template_renderer.template_directory

# NEW (unified):
install_dir = config.paths.installation.directory
log_dir = config.paths.runtime.logs
wallpapers = config.paths.host.wallpapers
templates = config.paths.project.templates
```

## Benefits Summary

1. **Single Source of Truth** - All paths in `config.paths.*`
2. **Robust Root Detection** - Marker-based, not fragile `.parent` chains
3. **Clear Organization** - Logical grouping (project, installation, host, runtime)
4. **All Defaults in TOML** - No Python default files to maintain
5. **Easy to Understand** - Clear hierarchy and structure
6. **Easy to Change** - Edit TOML, not code
7. **Resilient to Refactoring** - Project structure changes don't break paths


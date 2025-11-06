from pathlib import Path
from typing import Any, cast

from dotfiles_logging import LogLevels, validate_log_level_string
from pydantic import BaseModel, Field, field_validator

# Import defaults - must be after other imports to avoid circular dependency
from src.config.enums import InstallType
from src.config.project_root import get_project_root


def validate_boolean_string(value: str | bool) -> bool:
    """
    Validate and convert a string or boolean to bool.

    Args:
        value: String representation of boolean or boolean value

    Returns:
        bool value

    Raises:
        ValueError: If the boolean string is invalid
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized_value = value.lower()
        if normalized_value in ("true", "1", "yes", "on"):
            return True
        elif normalized_value in ("false", "0", "no", "off"):
            return False
        else:
            valid_options = "true, false, 1, 0, yes, no, on, off"
            raise ValueError(
                f"Invalid boolean value '{value}'. "
                f"Valid options are: {valid_options}"
            )

    raise ValueError(f"Cannot convert {type(value).__name__} to boolean")


class InstallDebugSettings(BaseModel):
    """Debug settings for installation.

    Defaults are loaded from defaults.toml [install.debug] section.
    """

    log_level: LogLevels = Field(
        default=LogLevels.ERROR, description="Log level"
    )
    output_to_file: bool = Field(
        default=False, description="Output log to file"
    )
    log_directory: Path = Field(
        default=Path.home() / "logs", description="Path to log directory"
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v: str | LogLevels) -> LogLevels:
        """Validate log level string matches LogLevelOptions."""
        if isinstance(v, str):
            return validate_log_level_string(v)
        return v

    @field_validator("output_to_file", mode="before")
    @classmethod
    def validate_output_to_file(cls, v: str | bool) -> bool:
        """Validate boolean string for output_to_file."""
        return validate_boolean_string(v)


# ============================================================================
# Path Config Classes
# ============================================================================

# Import defaults here to avoid circular dependency and IDE auto-removal
# Import PathTree early for type hints
from filesystem_path_builder import PathTree  # noqa: E402

from config import default_settings as defaults  # noqa: E402
from config import directories  # noqa: E402


class PathsConfig(BaseModel):
    """Unified paths configuration.

    Paths use ManagedPathTree for navigation and directory creation.

    Path definitions are defined in config/directories.py as the SINGLE
    SOURCE OF TRUTH. AppConfig.model_post_init() copies these definitions
    with the user's installation directory.

    To add new paths, edit config/directories.py:
        _install_builder.add_path("new_dir", hidden=True)

    Usage:
        # Navigate to paths
        config.project.paths.install.dotfiles.starship.path
        config.project.paths.install.dotfiles.nvim.lua.file("init.lua")
        config.project.paths.host.Pictures.wallpapers.path

        # Create all installation directories at once
        config.project.paths.install.create()

        # Get root installation path
        config.project.paths.install.path
    """

    model_config = {
        "arbitrary_types_allowed": True,  # Allow PathTree and ManagedPathTree
    }

    source: PathTree = Field(
        default=directories.src,
        description="Source paths (relative to project root)",
    )
    install: PathTree = Field(
        default=directories.install,
        description=(
            "Installation paths (ManagedPathTree with create() method)"
        ),
    )
    host: PathTree = Field(
        default=directories.host,
        description="Host system paths",
    )
    # runtime: PathTree = Field(
    #    default=directories.runtime,
    #    description="Runtime paths",
    # )

    @field_validator("install", "host", mode="before")
    @classmethod
    def ignore_dict_inputs(cls, v: Any) -> Any:
        """Ignore dict inputs from TOML and use defaults from directories.py.

        This validator ensures that any path configuration in TOML files
        is ignored, since paths are auto-generated from directories.py.
        """
        if isinstance(v, dict):
            # Return dummy value - Field default will be used instead
            return PathTree.from_str(Path.home())
        return v


class DirectoryDeletionSafetySettings(BaseModel):
    """Configuration for safe directory deletion."""

    protected_directories: list[str] = Field(
        default_factory=lambda: cast(
            list[str],
            defaults.DIRECTORY_DELETION_DEFAULTS["protected_directories"],
        ).copy(),
        description=(
            "List of protected directories that should never be deleted"
        ),
    )

    dangerous_keywords: list[str] = Field(
        default_factory=lambda: cast(
            list[str],
            defaults.DIRECTORY_DELETION_DEFAULTS["dangerous_keywords"],
        ).copy(),
        description="Keywords that make a path dangerous to delete",
    )

    minimum_path_depth: int = Field(
        default=cast(
            int, defaults.DIRECTORY_DELETION_DEFAULTS["minimum_path_depth"]
        ),
        ge=1,
        description="Minimum number of path segments required",
    )

    protect_user_homes: bool = Field(
        default=cast(
            bool, defaults.DIRECTORY_DELETION_DEFAULTS["protect_user_homes"]
        ),
        description="Whether to protect direct user home directories",
    )

    keyword_check_depth_threshold: int = Field(
        default=cast(
            int,
            defaults.DIRECTORY_DELETION_DEFAULTS[
                "keyword_check_depth_threshold"
            ],
        ),
        ge=2,
        description="Minimum depth for keyword checking "
        "(keywords only checked for shallow paths)",
    )


class PackageManagerSettings(BaseModel):
    """Package manager configuration settings."""

    prefer_third_party: bool = Field(
        default=defaults.PACKAGE_MANAGER_DEFAULTS["prefer_third_party"],
        description="Whether to prefer third-party repository helpers. "
        "On Arch: prefer paru/yay over pacman for AUR access. "
        "On Debian/RedHat: no effect (apt/dnf handle PPAs/COPR natively)",
    )

    update_system: bool = Field(
        default=defaults.PACKAGE_MANAGER_DEFAULTS["update_system"],
        description=(
            "Whether to update system packages before installing new ones"
        ),
    )

    remove_dependencies: bool = Field(
        default=defaults.PACKAGE_MANAGER_DEFAULTS["remove_dependencies"],
        description=(
            "Whether to remove unused dependencies when removing packages"
        ),
    )

    dry_run: bool = Field(
        default=defaults.PACKAGE_MANAGER_DEFAULTS["dry_run"],
        description=(
            "Only check for updates without applying them (dry run mode)"
        ),
    )


class SafetySettings(BaseModel):
    """Safety-related configuration settings."""

    directory_deletion: DirectoryDeletionSafetySettings = Field(
        default_factory=DirectoryDeletionSafetySettings,
        description="Directory deletion safety settings",
    )


class PackageConfigFile(BaseModel):
    """Configuration file specification for a package."""

    type: str = Field(
        description="Type of config: 'file' (static) or 'template' (Jinja2)"
    )
    path: Path = Field(description="Path to the config file or template")

    @field_validator("path", mode="before")
    @classmethod
    def resolve_relative_path(cls, v: str | Path) -> Path:
        """Resolve relative paths relative to project root.

        Package config paths in TOML are relative to project root.
        This validator converts them to absolute paths using get_project_root()
        which is set in main.py at application startup.

        Example:
            Input: "src/dotfiles/config-files/starship/starship.toml"
            Output: "/home/user/Development/new/src/dotfiles/
                config-files/starship/starship.toml"
        """
        path = Path(v)
        if not path.is_absolute():
            path = get_project_root() / path
        return path


class PluginPaths(BaseModel):
    """Plugin paths for zsh configuration."""

    model_config = {"extra": "allow"}  # Allow additional fields

    syntax_highlighting: str = Field(
        default="", description="Path to zsh-syntax-highlighting plugin"
    )
    autosuggestions: str = Field(
        default="", description="Path to zsh-autosuggestions plugin"
    )
    history_substring_search: str = Field(
        default="", description="Path to zsh-history-substring-search plugin"
    )
    fzf_key_bindings: str = Field(
        default="", description="Path to fzf key-bindings script"
    )
    fzf_completion: str = Field(
        default="", description="Path to fzf completion script"
    )


class PackageConfig(BaseModel):
    """Configuration for a specific package."""

    model_config = {"extra": "allow"}  # Allow additional fields

    conf: PackageConfigFile = Field(
        description="Configuration file specification",
    )
    plugin_paths: PluginPaths | None = Field(
        default=None,
        description="Plugin paths (for zsh package)",
    )

    @property
    def path(self) -> Path:
        """Convenience property to access conf.path directly."""
        return self.conf.path

    @property
    def type(self) -> str:
        """Convenience property to access conf.type directly."""
        return self.conf.type


class Feature(BaseModel):
    """Feature configuration with version and other properties.

    This model represents a single feature (e.g., python, nodejs, rust)
    with its configuration. The feature name is stored as the dict key,
    not in this model.

    Example TOML:
        [project.settings.system.packages.features]
        python = { version = "3.12.0", pip_packages = ["ipython", "black"] }
        nodejs = { version = "20.9.0" }

    This maps to:
        features["python"] = Feature(
            version="3.12.0", pip_packages=["ipython", "black"]
        )
        features["nodejs"] = Feature(version="20.9.0")
    """

    version: str = Field(description="Version of the feature")
    pip_packages: list[str] = Field(
        default_factory=list,
        description="List of pip packages to install (for Python features)",
    )


class PackageConfigDict(dict[str, PackageConfig]):
    """Dictionary that supports both dict['key'] and dict.key attribute
    access."""

    def __getattr__(self, name: str) -> PackageConfig:
        """Allow attribute access to package configs."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"Package config '{name}' not found. "
                f"Available configs: {list(self.keys())}"
            ) from None

    def __setattr__(self, name: str, value: PackageConfig) -> None:
        """Allow attribute assignment to package configs."""
        self[name] = value


class SystemPackages(BaseModel):
    """System packages configuration."""

    packages: list[str] = Field(
        default_factory=list, description="List of system packages to install"
    )
    config: dict[str, PackageConfig] = Field(
        default_factory=dict,
        description="Package-specific configuration (e.g., zsh, tmux)",
    )
    features: dict[str, Feature] = Field(
        default_factory=dict,
        description="Features to install with versions (e.g., python, nodejs)",
    )

    def model_post_init(self, __context: Any) -> None:
        """Convert config dict to PackageConfigDict after validation."""
        if not isinstance(self.config, PackageConfigDict):
            # Convert regular dict to PackageConfigDict
            new_config = PackageConfigDict()
            for pkg_name, pkg_config in self.config.items():
                new_config[pkg_name] = pkg_config
            # Use object.__setattr__ to bypass Pydantic's validation
            object.__setattr__(self, "config", new_config)

    @field_validator("config", mode="before")
    @classmethod
    def convert_raw_config_to_package_config(
        cls, v: dict[str, Any] | PackageConfigDict
    ) -> dict[str, PackageConfig]:
        """Convert raw config dicts to PackageConfig objects.

        Handles conversion of TOML structure like:
        [config.zsh]
        type = "template"
        path = "..."
        [config.zsh.plugin_paths]
        syntax_highlighting = "..."

        Into PackageConfig(
            conf=PackageConfigFile(type="template", path="..."),
            plugin_paths=PluginPaths(syntax_highlighting="...")
        )
        """
        if isinstance(v, PackageConfigDict):
            return dict(v)

        # Convert each package config dict to PackageConfig object
        result: dict[str, PackageConfig] = {}
        for pkg_name, pkg_data in v.items():
            if isinstance(pkg_data, PackageConfig):
                result[pkg_name] = pkg_data
            elif isinstance(pkg_data, dict):
                # Extract plugin_paths if present
                plugin_paths_data = pkg_data.pop("plugin_paths", None)
                plugin_paths = None
                if plugin_paths_data:
                    plugin_paths = PluginPaths(**plugin_paths_data)

                # If dict has 'type' and 'path', wrap in PackageConfig
                if "type" in pkg_data and "path" in pkg_data:
                    result[pkg_name] = PackageConfig(
                        conf=PackageConfigFile(
                            type=pkg_data["type"], path=pkg_data["path"]
                        ),
                        plugin_paths=plugin_paths,
                    )
                else:
                    # Assume it's already in the right format
                    result[pkg_name] = PackageConfig(
                        **pkg_data, plugin_paths=plugin_paths
                    )
            else:
                result[pkg_name] = pkg_data

        return result


class System(BaseModel):
    """System-level configuration."""

    packages: SystemPackages = Field(
        default_factory=SystemPackages,
        description="System packages configuration",
    )


class ContainerManagerSettings(BaseModel):
    """Container manager configuration settings."""

    runtime: str = Field(
        default=cast(str, defaults.CONTAINER_MANAGER_DEFAULTS["runtime"]),
        description="Container runtime to use (docker or podman)",
    )

    build_timeout: int = Field(
        default=cast(
            int, defaults.CONTAINER_MANAGER_DEFAULTS["build_timeout"]
        ),
        description="Container build timeout in seconds",
    )

    default_registry: str = Field(
        default=cast(
            str, defaults.CONTAINER_MANAGER_DEFAULTS["default_registry"]
        ),
        description="Default container registry",
    )

    cache_enabled: bool = Field(
        default=cast(
            bool, defaults.CONTAINER_MANAGER_DEFAULTS["cache_enabled"]
        ),
        description="Enable build cache",
    )


class TemplateRendererSettings(BaseModel):
    """Template renderer configuration settings.

    Note: template_directory is now managed through paths.source.templates
    and resolved at runtime using get_project_root().
    """

    strict_mode: bool = Field(
        default=defaults.TEMPLATE_RENDERER_DEFAULTS["strict_mode"],
        description="Fail on missing template variables",
    )


class CliSettings(BaseModel):
    """User-configurable CLI settings.

    These are settings that the user can override via:
    - CLI arguments (highest priority)
    - User settings.toml (project root)
    - Project settings.toml (cli/config)
    - defaults.toml (cli/config)
    """

    installation_directory: Path = Field(
        default=Path.home() / "dotfiles",
        description="Directory where dotfiles will be installed",
    )
    backup_directory: Path = Field(
        default=Path.home() / "backup",
        description="Directory for backing up existing dotfiles",
    )
    install_type: InstallType = Field(
        default=InstallType.update,
        description="Type of installation (update or clean)",
    )
    hidden: bool = Field(
        default=True,
        description="Hide the installation directory",
    )
    debug: InstallDebugSettings = Field(
        default_factory=InstallDebugSettings,
        description="Debug settings (log level, output to file, etc.)",
    )

    @field_validator("installation_directory")
    @classmethod
    def validate_installation_directory(cls, v: Path) -> Path:
        """Ensure installation directory is not the placeholder value."""
        placeholder = Path.home() / ".tmp" / "dotfiles-placeholder"
        if v == placeholder:
            raise ValueError(
                "Installation directory cannot be the placeholder value. "
                "This indicates a configuration error - the installation "
                "directory must be set via CLI arguments, settings.toml, "
                "or defaults.toml."
            )
        return v

    @field_validator("hidden", mode="before")
    @classmethod
    def validate_hidden(cls, v: str | bool) -> bool:
        """Validate boolean string for hidden."""
        return validate_boolean_string(v)


class ProjectSettings(BaseModel):
    """Project-level settings (not user-configurable)."""

    package_manager: PackageManagerSettings = Field(
        default_factory=PackageManagerSettings,
        description="Package manager configuration",
    )
    safety: SafetySettings = Field(
        default_factory=SafetySettings,
        description="Safety configuration (protected directories, etc.)",
    )
    template_renderer: TemplateRendererSettings = Field(
        default_factory=TemplateRendererSettings,
        description="Template renderer configuration",
    )
    container_manager: ContainerManagerSettings = Field(
        default_factory=ContainerManagerSettings,
        description="Container manager configuration",
    )
    system: System = Field(
        default_factory=System,
        description="System configuration (packages, etc.)",
    )


class ProjectConfig(BaseModel):
    """Project/CLI configuration (how the CLI works).

    This contains all the configuration for how the CLI operates,
    including paths, templates, container manager, system settings, etc.
    """

    paths: PathsConfig = Field(
        default_factory=PathsConfig,
        description="All paths (source, installation, host, runtime)",
    )
    settings: ProjectSettings = Field(
        default_factory=ProjectSettings,
        description="Project-level settings (not user-configurable)",
    )


class AppConfig(BaseModel):
    """Application configuration.

    Configuration hierarchy (highest to lowest priority):
    1. CLI arguments (passed at runtime)
    2. User settings.toml (project root)
    3. Project settings.toml (cli/config)
    4. defaults.toml (cli/config)

    Structure:
    - cli_settings: User-configurable settings (install dir, backup dir,
        type, etc.)
    - project: Project/CLI configuration (paths, templates, container
        manager, etc.)
      - project.paths.source: This project's source files
      - project.paths.installation: Target installation paths (where
          dotfiles go)
      - project.paths.host: User's system directories
      - project.paths.runtime: Logs, cache, etc.
    """

    cli_settings: CliSettings = Field(
        default_factory=CliSettings,
        description="User-configurable CLI settings",
    )

    project: ProjectConfig = Field(
        default_factory=ProjectConfig,
        description="Project/CLI configuration",
    )

    def model_post_init(self, __context: Any) -> None:
        """Set up cross-references after initialization."""
        # Sync user's installation directory to project paths
        from filesystem_path_builder import PathsBuilder

        # Regenerate install paths with user's installation directory
        install_root = self.cli_settings.installation_directory

        # Create new builder with user's installation directory
        # Copy all path definitions from directories.install_builder
        # This ensures directories.py is the SINGLE SOURCE OF TRUTH
        # Use strict=True to match the original builder's strict mode
        builder = PathsBuilder(install_root, strict=True)
        for (
            _key,
            definition,
        ) in directories.install_builder.definitions.items():
            # Use original_key to preserve hyphens, spaces, and case in directory names
            builder.add_path(definition.original_key, hidden=definition.hidden)

        # Build returns ManagedPathTree with create() and navigation
        self.project.paths.install = builder.build()

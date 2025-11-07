from pathlib import Path
from typing import Any, Literal

from dotfiles_logging.rich.rich_logger import RichLogger
from dotfiles_package_manager.core.base import (
    PackageManager,
    PackageManagerError,
)
from dotfiles_package_manager.core.factory import PackageManagerFactory
from dotfiles_pipeline import PipelineContext
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig

from src.config.enums import InstallType
from src.exceptions import InstallationConfirmationDeclinedException
from src.tasks.install_starship import (
    StarshipInstallError,
    check_starship_installed,
    get_starship_version,
    install_starship,
)
from src.utils import file_manager
from src.utils.config_model_registry import ConfigModelRegistry
from src.utils.file_manager import (
    delete_directory_safe,
    get_file_hash,
)
from src.utils.settings_override import (
    SettingsOverrideError,
    SettingsOverrider,
)


def detect_and_initialize_package_manager(
    context: PipelineContext,
) -> PipelineContext:
    """Detect and initialize the package manager.

    Args:
        context: The pipeline context

    Returns:
        Updated pipeline context with package manager initialized

    Raises:
        PackageManagerError: If package manager detection fails
    """
    try:
        # Get settings from config
        pm_settings = context.app_config.project.settings.package_manager
        prefer_third_party = pm_settings.prefer_third_party

        # Auto-detect best available manager
        package_manager = PackageManagerFactory.create_auto(
            prefer_third_party=prefer_third_party
        )
        manager_type = package_manager.manager_type.value
        context.logger_instance.debug(
            f"Auto-detected package manager: {manager_type}"
        )

        # Store package manager in context (using dedicated field)
        context.package_manager = package_manager
        # Store type in results for informational purposes
        context.results["package_manager_type"] = package_manager.manager_type

        # Log available managers for debugging
        available = PackageManagerFactory.get_available_managers()
        context.logger_instance.debug(
            f"Available package managers: {[m.value for m in available]}"
        )

    except PackageManagerError as e:
        context.logger_instance.error(
            f"Failed to initialize package manager: {e}"
        )
        context.errors.append(e)
        raise

    return context


def handle_previous_installation(context: PipelineContext) -> PipelineContext:
    """Handle previous installation based on install type."""
    install_type: InstallType = context.app_config.cli_settings.install_type
    install_directory: Path = context.app_config.project.paths.install.path
    dotfiles_directory: Path = (
        context.app_config.project.paths.install.dotfiles.path
    )
    try:
        match install_type:
            case InstallType.clean:
                context = handle_clean_installation(context, install_directory)
            case InstallType.update:
                context = handle_update_installation(
                    context, dotfiles_directory
                )
            case _:
                raise ValueError(f"Unknown install type: {install_type}")
    except Exception as e:
        context.logger_instance.error(
            f"Failed to handle {install_type.value} installation: {e}"
        )
        context.errors.append(e)
        # Re-raise to stop pipeline execution for critical errors
        raise

    return context


def backup_previous_installation(context: PipelineContext) -> PipelineContext:
    install_directory: Path = context.app_config.project.paths.install.path
    backup_directory: Path = context.app_config.cli_settings.backup_directory

    try:
        file_manager.copy_directory_filtered(
            src_path=install_directory,
            dest_path=backup_directory,
        )
        context.logger_instance.info(
            f"Previous installation backed up to {backup_directory}"
        )
    except Exception as e:
        context.logger_instance.error(
            f"Failed to backup previous installation: {e}"
        )
        context.errors.append(e)
    return context


def confirm_overwrite_previous_installation(context: PipelineContext) -> bool:
    install_directory: Path = context.app_config.project.paths.install.path

    confirmation_message = (
        f"[bold yellow]Overwrite previous installation at "
        f"[/bold yellow]'{install_directory}'?",
        "This will delete all files in the previous installation directory.",
    )
    overwrite_previous_installation: bool = context.logger_instance.confirm(
        "\n".join(confirmation_message),
        default=False,
    )
    return overwrite_previous_installation


def confirm_backup(context: PipelineContext) -> bool:
    backup_install_directory: bool = context.logger_instance.confirm(
        "[bold yellow]Do you want to backup the contents of the previous "
        "installation directory?[/bold yellow]",
        default=True,
    )
    return backup_install_directory


def handle_clean_installation(
    context: PipelineContext, install_directory: Path
) -> PipelineContext:
    from src.utils import file_manager
    from src.utils.file_manager import has_any_contents, is_directory_empty

    install_type = context.app_config.cli_settings.install_type

    context.logger_instance.debug(
        f"Performing {install_type.value} installation"
    )
    if not is_directory_empty(
        install_directory
    ) and not confirm_overwrite_previous_installation(context):
        raise InstallationConfirmationDeclinedException(
            "User declined to overwrite previous installation"
        )

    if has_any_contents(install_directory) and confirm_backup(context):
        backup_previous_installation(context)

    # Delete the installation directory safely
    try:
        context.logger_instance.debug(
            f"Deleting installation directory: {install_directory}"
        )
        file_manager.delete_directory_safe(install_directory)
        context.logger_instance.debug(
            "Installation directory deleted successfully"
        )
    except Exception as e:
        context.logger_instance.error(
            f"Failed to delete installation directory: {e}"
        )
        context.errors.append(e)

    return context


def handle_update_installation(
    context: PipelineContext, dir_to_delete: Path
) -> PipelineContext:
    install_type = context.app_config.cli_settings.install_type
    context.logger_instance.debug(
        f"Performing {install_type.value} installation"
    )
    try:
        context.logger_instance.debug(f"Deleting directory: {dir_to_delete}")
        file_manager.delete_directory_safe(dir_to_delete)
    except FileNotFoundError:
        pass
    except Exception as e:
        context.errors.append(e)
    return context


def update_system_packages(context: PipelineContext) -> PipelineContext:
    """Update system packages.

    Args:
        context: The pipeline context

    Returns:
        Updated pipeline context with system update results

    Note:
        Assumes DetectPackageManagerStep has run successfully.
        Pipeline will have stopped if package manager detection failed.
    """
    # Get settings from config
    pm_settings = context.app_config.project.settings.package_manager
    update_system = pm_settings.update_system
    dry_run = pm_settings.dry_run

    # Skip if update_system is disabled
    if not update_system:
        context.logger_instance.debug(
            "System update disabled in settings, skipping"
        )
        context.results["system_update_skipped"] = True
        return context

    # Package manager is guaranteed to exist if we reached this step
    pm: PackageManager = context.package_manager  # type: ignore[assignment]

    try:
        if dry_run:
            context.logger_instance.debug("Checking for system updates...")
        else:
            context.logger_instance.debug("Updating system packages...")

        result = pm.update_system(dry_run=dry_run)

        if result.success:
            context.logger_instance.debug(
                f"System update check completed: {result.output}"
            )
            context.results["system_update_success"] = True
        else:
            msg = (
                f"System update completed with issues: {result.error_message}"
            )
            context.logger_instance.warning(msg)
            context.results["system_update_success"] = False

        context.results["system_update_result"] = result

    except PackageManagerError as e:
        context.logger_instance.error(f"System update failed: {e}")
        context.errors.append(e)
        context.results["system_update_success"] = False

    return context


def install_packages(context: PipelineContext) -> PipelineContext:
    """Install system packages.

    Args:
        context: The pipeline context

    Returns:
        Updated pipeline context with installation results

    Note:
        Assumes DetectPackageManagerStep has run successfully.
        Pipeline will have stopped if package manager detection failed.
        System update should be handled by UpdateSystemStep before this step.
    """
    # Get packages from config
    packages = context.app_config.project.settings.system.packages.packages

    if not packages:
        context.logger_instance.debug("No packages to install")
        return context

    # Package manager is guaranteed to exist if we reached this step
    pm: PackageManager = context.package_manager  # type: ignore[assignment]

    try:
        context.logger_instance.debug(
            f"Installing packages: {', '.join(packages)}"
        )
        # Don't update system here - rely on UpdateSystemStep
        result = pm.install(packages, update_system=False)

        if result.success:
            if result.packages_installed:
                installed = ", ".join(result.packages_installed)
                msg = f"Successfully installed: {installed}"
                context.logger_instance.debug(msg)
            if result.packages_failed:
                failed = ", ".join(result.packages_failed)
                msg = f"Failed to install: {failed}"
                context.logger_instance.warning(msg)
        else:
            msg = f"Package installation failed: {result.error_message}"
            context.logger_instance.error(msg)

        # Store results
        context.results["install_result"] = result

        # Track overall installation success
        if "packages_installed" not in context.results:
            context.results["packages_installed"] = []
        if "packages_failed" not in context.results:
            context.results["packages_failed"] = []

        context.results["packages_installed"].extend(result.packages_installed)
        context.results["packages_failed"].extend(result.packages_failed)

    except PackageManagerError as e:
        context.logger_instance.error(f"Package installation failed: {e}")
        context.errors.append(e)

        # Track failed packages
        if "packages_failed" not in context.results:
            context.results["packages_failed"] = []
        context.results["packages_failed"].extend(packages)

    return context


def _sync_starship_config(
    config_source: Path,
    config_dest: Path,
    logger: RichLogger,
) -> bool:
    """Sync starship config from source to destination.

    Args:
        config_source: Source config file path
        config_dest: Destination config file path
        logger: Logger instance

    Returns:
        True if config was synced, False if already up to date
    """
    if not config_dest.exists():
        try:
            config_dest.write_text(config_source.read_text())
            logger.debug(f"Starship config created at {config_dest}")
            return True
        except Exception as e:
            logger.error(f"Failed to create starship config: {e}")
            raise

    source_hash = get_file_hash(config_source)
    dest_hash = get_file_hash(config_dest)

    if source_hash != dest_hash:
        logger.debug("Starship config out of date, updating...")
        delete_directory_safe(config_dest)
        config_dest.write_text(config_source.read_text())
        return True

    logger.debug(f"Starship config at '{config_dest}' is up to date")
    return False


def _handle_starship_already_installed(
    context: PipelineContext,
    force: bool,
) -> bool:
    """Check if Starship is already installed and handle accordingly.

    Args:
        context: The pipeline context
        force: Whether to force reinstallation

    Returns:
        True if Starship is already installed and should skip installation
    """
    if force or not check_starship_installed():
        return False

    logger = context.logger_instance
    version = get_starship_version()
    logger.debug(f"Starship is already installed (version: {version})")

    context.results["starship_installed"] = True
    context.results["starship_version"] = version
    context.results["starship_already_present"] = True

    return True


def _perform_starship_installation(
    context: PipelineContext,
    timeout: int,
) -> None:
    """Perform the actual Starship installation.

    Args:
        context: The pipeline context
        timeout: Installation timeout in seconds

    Raises:
        StarshipInstallError: If installation fails
    """
    logger = context.logger_instance
    logger.debug("Installing Starship prompt...")
    install_starship(force=False, timeout=timeout)

    version = get_starship_version()
    logger.debug(f"Successfully installed Starship (version: {version})")

    context.results["starship_installed"] = True
    context.results["starship_version"] = version
    context.results["starship_already_present"] = False


def install_starship_prompt(
    context: PipelineContext,
    force: bool = False,
    timeout: int = 300,
    critical: bool = False,
) -> PipelineContext:
    """Install Starship prompt with config management.

    Args:
        context: The pipeline context
        force: Force reinstallation even if already installed
        timeout: Installation timeout in seconds (default: 300)
        critical: Whether failure should stop the pipeline (default: False)

    Returns:
        Updated pipeline context with installation results

    Raises:
        StarshipInstallError: If installation fails and critical is True
    """
    logger = context.logger_instance

    # Get config paths
    starship_config = (
        context.app_config.project.settings.system.packages.config.starship
    )
    config_source: Path = starship_config.path
    config_dest: Path = (
        context.app_config.project.paths.install.dotfiles.starship.file(
            "starship.toml"
        )
    )

    # Handle already installed case
    if _handle_starship_already_installed(context, force):
        try:
            _sync_starship_config(config_source, config_dest, logger)
        except Exception as e:
            logger.error(f"Failed to sync starship config: {e}")
            context.errors.append(e)
        return context

    # Perform installation
    try:
        _perform_starship_installation(context, timeout)
        _sync_starship_config(config_source, config_dest, logger)

    except StarshipInstallError as e:
        logger.error(f"Failed to install Starship: {e.message}")
        context.errors.append(e)
        context.results["starship_installed"] = False

        if critical:
            raise

    return context


def render_zsh_config(context: PipelineContext) -> PipelineContext:
    """Render Zsh configuration from template.

    Args:
        context: The pipeline context

    Returns:
        Updated pipeline context with rendering results

    Raises:
        TemplateRenderError: If template rendering fails
    """
    logger = context.logger_instance

    # Get zsh package config
    zsh_config = dict(
        context.app_config.project.settings.system.packages.config
    ).get("zsh")
    if not zsh_config:
        logger.warning("No Zsh configuration found, skipping")
        return context

    # Extract paths
    template_path: Path = zsh_config.path
    template_dir: Path = template_path.parent
    template_name: str = template_path.name

    zshrc_path: Path = (
        context.app_config.project.paths.install.dotfiles.zsh.file("zshrc")
    )
    oh_my_zsh_path: Path = (
        context.app_config.project.paths.install.dependencies["oh-my-zsh"].path
    )
    cache_dir: Path = context.app_config.project.paths.host.cache.path
    nvm_path: Path = (
        context.app_config.project.paths.install.dependencies.nvm.path
    )
    pyenv_path: Path = (
        context.app_config.project.paths.install.dependencies.pyenv.path
    )
    starship_config_path: Path = (
        context.app_config.project.paths.install.dotfiles.starship.file(
            "starship.toml"
        )
    )

    # Get distro-specific plugin paths
    plugin_paths = {}
    if zsh_config.plugin_paths is not None:
        plugin_paths = {
            "ZSH_SYNTAX_HIGHLIGHTING": (
                zsh_config.plugin_paths.syntax_highlighting
            ),
            "ZSH_AUTOSUGGESTIONS": (zsh_config.plugin_paths.autosuggestions),
            "ZSH_HISTORY_SUBSTRING_SEARCH": (
                zsh_config.plugin_paths.history_substring_search
            ),
            "FZF_KEY_BINDINGS": zsh_config.plugin_paths.fzf_key_bindings,
            "FZF_COMPLETION": zsh_config.plugin_paths.fzf_completion,
        }
        logger.debug(f"Using distro-specific plugin paths: {plugin_paths}")
    else:
        # Fallback to Arch paths if plugin_paths not configured
        logger.warning(
            "No plugin_paths configured for zsh, using Arch defaults"
        )
        plugin_paths = {
            "ZSH_SYNTAX_HIGHLIGHTING": (
                "/usr/share/zsh/plugins/zsh-syntax-highlighting/"
                "zsh-syntax-highlighting.zsh"
            ),
            "ZSH_AUTOSUGGESTIONS": (
                "/usr/share/zsh/plugins/zsh-autosuggestions/"
                "zsh-autosuggestions.zsh"
            ),
            "ZSH_HISTORY_SUBSTRING_SEARCH": (
                "/usr/share/zsh/plugins/zsh-history-substring-search/"
                "zsh-history-substring-search.zsh"
            ),
            "FZF_KEY_BINDINGS": "/usr/share/fzf/key-bindings.zsh",
            "FZF_COMPLETION": "/usr/share/fzf/completion.zsh",
        }

    # Check if pyenv feature is configured
    features = context.app_config.project.settings.system.packages.features
    pyenv_configured = "pyenv" in features

    # Build template variables
    variables = {
        "STARSHIP_CONFIG": str(starship_config_path),
        "OH_MY_ZSH_DIR": str(oh_my_zsh_path),
        "CACHE_DIR": str(cache_dir),
        "NVM_DIR": str(nvm_path),
        "PYENV_DIR": str(pyenv_path),
        "PYENV_CONFIGURED": pyenv_configured,
        **plugin_paths,  # Add plugin paths
    }

    try:
        # Get template renderer configuration
        strict_mode = (
            context.app_config.project.settings.template_renderer.strict_mode
        )
        render_config = RenderConfig(strict_mode=strict_mode)

        # Initialize renderer
        logger.debug(f"Rendering Zsh config from template: {template_path}")
        renderer = Jinja2Renderer(template_dir, config=render_config)

        # Render template to file
        renderer.render_to_file(template_name, zshrc_path, variables=variables)

        logger.debug(f"Successfully rendered Zsh config to {zshrc_path}")
        context.results["zsh_config_rendered"] = True

    except Exception as e:
        logger.error(f"Failed to render Zsh config: {e}")
        context.errors.append(e)
        context.results["zsh_config_rendered"] = False
        raise

    return context


def install_oh_my_zsh_framework(
    context: PipelineContext,
    force: bool = False,
    timeout: int = 300,
    critical: bool = True,
) -> PipelineContext:
    """Install Oh My Zsh framework.

    Args:
        context: The pipeline context
        force: Force reinstallation even if already installed
        timeout: Installation timeout in seconds (default: 300)
        critical: Whether failure should stop the pipeline (default: True)

    Returns:
        Updated pipeline context with installation results

    Raises:
        OhMyZshInstallError: If installation fails and critical is True
    """
    from src.tasks.install_oh_my_zsh import (
        OhMyZshInstallError,
        check_oh_my_zsh_installed,
        get_oh_my_zsh_version,
        install_oh_my_zsh,
    )

    logger = context.logger_instance

    # Get Oh My Zsh directory from config
    oh_my_zsh_dir: Path = (
        context.app_config.project.paths.install.dependencies["oh-my-zsh"].path
    )

    # Handle already installed case
    if not force and check_oh_my_zsh_installed(oh_my_zsh_dir):
        version = get_oh_my_zsh_version(oh_my_zsh_dir)
        logger.debug(f"Oh My Zsh already installed (version: {version})")
        context.results["oh_my_zsh_installed"] = True
        context.results["oh_my_zsh_version"] = version
        context.results["oh_my_zsh_already_present"] = True
        return context

    # Perform installation
    try:
        logger.debug("Installing Oh My Zsh framework...")
        install_oh_my_zsh(oh_my_zsh_dir, force=force, timeout=timeout)

        version = get_oh_my_zsh_version(oh_my_zsh_dir)
        logger.debug(f"Successfully installed Oh My Zsh (version: {version})")

        context.results["oh_my_zsh_installed"] = True
        context.results["oh_my_zsh_version"] = version
        context.results["oh_my_zsh_already_present"] = False

    except OhMyZshInstallError as e:
        logger.error(f"Failed to install Oh My Zsh: {e.message}")
        context.errors.append(e)
        context.results["oh_my_zsh_installed"] = False

        if critical:
            raise

    return context


def install_nvm_manager(
    context: PipelineContext,
    force: bool = False,
    timeout: int = 300,
    critical: bool = True,
) -> PipelineContext:
    """Install NVM (Node Version Manager).

    Args:
        context: The pipeline context
        force: Force reinstallation even if already installed
        timeout: Installation timeout in seconds (default: 300)
        critical: Whether failure should stop the pipeline (default: True)

    Returns:
        Updated pipeline context with installation results

    Raises:
        NvmInstallError: If installation fails and critical is True
    """
    from src.tasks.install_nvm import (
        NvmInstallError,
        check_nvm_installed,
        get_nvm_version,
        install_nvm,
    )

    logger = context.logger_instance

    # Get NVM configuration
    features = context.app_config.project.settings.system.packages.features
    if "nvm" not in features:
        logger.debug("NVM feature not configured, skipping installation")
        context.results["nvm_installed"] = False
        context.results["nvm_skipped"] = True
        return context

    nvm_version = features["nvm"].version
    nvm_dir: Path = (
        context.app_config.project.paths.install.dependencies.nvm.path
    )

    # Handle already installed case
    if not force and check_nvm_installed(nvm_dir):
        version = get_nvm_version(nvm_dir)
        logger.debug(f"NVM already installed (version: {version})")
        context.results["nvm_installed"] = True
        context.results["nvm_version"] = version
        context.results["nvm_already_present"] = True
        return context

    # Perform installation
    try:
        logger.debug(f"Installing NVM version {nvm_version}...")
        install_nvm(nvm_dir, version=nvm_version, force=force, timeout=timeout)

        version = get_nvm_version(nvm_dir)
        logger.debug(f"Successfully installed NVM (version: {version})")

        context.results["nvm_installed"] = True
        context.results["nvm_version"] = version
        context.results["nvm_already_present"] = False

    except NvmInstallError as e:
        logger.error(f"Failed to install NVM: {e.message}")
        context.errors.append(e)
        context.results["nvm_installed"] = False

        if critical:
            raise

    return context


def install_nodejs_runtime(
    context: PipelineContext,
    timeout: int = 600,
    critical: bool = True,
) -> PipelineContext:
    """Install Node.js using NVM.

    Args:
        context: The pipeline context
        timeout: Installation timeout in seconds (default: 600)
        critical: Whether failure should stop the pipeline (default: True)

    Returns:
        Updated pipeline context with installation results

    Raises:
        NodejsInstallError: If installation fails and critical is True
    """
    from src.tasks.install_nodejs import (
        NodejsInstallError,
        check_nodejs_installed,
        get_nodejs_version,
        install_nodejs_with_nvm,
    )

    logger = context.logger_instance

    # Get Node.js configuration
    features = context.app_config.project.settings.system.packages.features

    # Check if Node.js feature is configured
    if "nodejs" not in features:
        logger.debug("Node.js feature not configured, skipping installation")
        context.results["nodejs_installed"] = False
        context.results["nodejs_skipped"] = True
        return context

    # Check if NVM feature is also configured (required for Node.js)
    if "nvm" not in features:
        error_msg = (
            "Node.js feature is configured but NVM feature is not. "
            "NVM is required to install Node.js. "
            "Please add 'nvm = { version = \"0.40.3\" }' to features."
        )
        logger.error(error_msg)
        error = NodejsInstallError(error_msg)
        context.errors.append(error)
        context.results["nodejs_installed"] = False

        if critical:
            raise error

        return context

    # Check if NVM was successfully installed
    if not context.results.get("nvm_installed", False):
        error_msg = (
            "Cannot install Node.js because NVM installation failed or "
            "was skipped. Please ensure NVM is installed first."
        )
        logger.error(error_msg)
        error = NodejsInstallError(error_msg)
        context.errors.append(error)
        context.results["nodejs_installed"] = False

        if critical:
            raise error

        return context

    nodejs_version = features["nodejs"].version
    nvm_dir: Path = (
        context.app_config.project.paths.install.dependencies.nvm.path
    )

    # Handle already installed case
    if check_nodejs_installed(nvm_dir, nodejs_version):
        version = get_nodejs_version(nvm_dir)
        logger.debug(f"Node.js already installed (version: {version})")
        context.results["nodejs_installed"] = True
        context.results["nodejs_version"] = version
        context.results["nodejs_already_present"] = True
        return context

    # Perform installation
    try:
        logger.debug(
            f"Installing Node.js version {nodejs_version} using NVM..."
        )
        install_nodejs_with_nvm(
            nvm_dir, version=nodejs_version, set_default=True, timeout=timeout
        )

        version = get_nodejs_version(nvm_dir)
        logger.debug(f"Successfully installed Node.js (version: {version})")

        context.results["nodejs_installed"] = True
        context.results["nodejs_version"] = version
        context.results["nodejs_already_present"] = False

    except NodejsInstallError as e:
        logger.error(f"Failed to install Node.js: {e.message}")
        context.errors.append(e)
        context.results["nodejs_installed"] = False

        if critical:
            raise

    return context


def install_pyenv_manager(
    context: PipelineContext,
    force: bool = False,
    timeout: int = 300,
    critical: bool = True,
) -> PipelineContext:
    """Install pyenv (Python Version Manager).

    Args:
        context: The pipeline context
        force: Force reinstallation even if already installed
        timeout: Installation timeout in seconds (default: 300)
        critical: Whether failure should stop the pipeline (default: True)

    Returns:
        Updated pipeline context with installation results

    Raises:
        PyenvInstallError: If installation fails and critical is True
    """
    from src.tasks.install_pyenv import (
        PyenvInstallError,
        check_pyenv_installed,
        get_pyenv_version,
        install_pyenv,
    )

    logger = context.logger_instance

    # Get pyenv configuration
    features = context.app_config.project.settings.system.packages.features
    if "pyenv" not in features:
        logger.debug("Pyenv feature not configured, skipping installation")
        context.results["pyenv_installed"] = False
        context.results["pyenv_skipped"] = True
        return context

    pyenv_dir: Path = (
        context.app_config.project.paths.install.dependencies.pyenv.path
    )

    # Handle already installed case
    if not force and check_pyenv_installed(pyenv_dir):
        version = get_pyenv_version(pyenv_dir)
        logger.debug(f"Pyenv already installed (version: {version})")
        context.results["pyenv_installed"] = True
        context.results["pyenv_version"] = version
        context.results["pyenv_already_present"] = True
        return context

    # Perform installation
    try:
        logger.debug("Installing pyenv (latest version)...")
        install_pyenv(pyenv_dir, timeout=timeout)

        version = get_pyenv_version(pyenv_dir)
        logger.debug(f"Successfully installed pyenv (version: {version})")

        context.results["pyenv_installed"] = True
        context.results["pyenv_version"] = version
        context.results["pyenv_already_present"] = False

    except PyenvInstallError as e:
        logger.error(f"Failed to install pyenv: {e.message}")
        context.errors.append(e)
        context.results["pyenv_installed"] = False

        if critical:
            raise

    return context


def install_python_runtime(
    context: PipelineContext,
    timeout: int = 600,
    critical: bool = True,
) -> PipelineContext:
    """Install Python using pyenv.

    Args:
        context: The pipeline context
        timeout: Installation timeout in seconds (default: 600)
        critical: Whether failure should stop the pipeline (default: True)

    Returns:
        Updated pipeline context with installation results

    Raises:
        PythonInstallError: If installation fails and critical is True
    """
    from src.tasks.install_python import (
        PythonInstallError,
        check_python_installed,
        get_python_version,
        install_python_with_pyenv,
    )

    logger = context.logger_instance

    # Get Python configuration
    features = context.app_config.project.settings.system.packages.features

    # Check if Python feature is configured
    if "python" not in features:
        logger.debug("Python feature not configured, skipping installation")
        context.results["python_installed"] = False
        context.results["python_skipped"] = True
        return context

    # Check if pyenv feature is also configured (required for Python)
    if "pyenv" not in features:
        error_msg = (
            "Python feature is configured but pyenv feature is not. "
            "Pyenv is required to install Python. "
            "Please add 'pyenv = { version = \"2.4.17\" }' to features."
        )
        logger.error(error_msg)
        error = PythonInstallError(error_msg)
        context.errors.append(error)
        context.results["python_installed"] = False

        if critical:
            raise error

        return context

    # Check if pyenv was successfully installed
    if not context.results.get("pyenv_installed", False):
        error_msg = (
            "Cannot install Python because pyenv installation failed or "
            "was skipped. Please ensure pyenv is installed first."
        )
        logger.error(error_msg)
        error = PythonInstallError(error_msg)
        context.errors.append(error)
        context.results["python_installed"] = False

        if critical:
            raise error

        return context

    python_version = features["python"].version
    pyenv_dir: Path = (
        context.app_config.project.paths.install.dependencies.pyenv.path
    )

    # Handle already installed case
    if check_python_installed(pyenv_dir, python_version):
        version = get_python_version(pyenv_dir)
        logger.debug(f"Python already installed (version: {version})")
        context.results["python_installed"] = True
        context.results["python_version"] = version
        context.results["python_already_present"] = True
        return context

    # Perform installation
    try:
        logger.debug(
            f"Installing Python version {python_version} using pyenv..."
        )
        install_python_with_pyenv(
            pyenv_dir, version=python_version, timeout=timeout
        )

        version = get_python_version(pyenv_dir)
        logger.debug(f"Successfully installed Python (version: {version})")

        context.results["python_installed"] = True
        context.results["python_version"] = version
        context.results["python_already_present"] = False

    except PythonInstallError as e:
        logger.error(f"Failed to install Python: {e.message}")
        context.errors.append(e)
        context.results["python_installed"] = False

        if critical:
            raise

    return context


def install_pip_packages_runtime(
    context: PipelineContext,
    timeout: int = 600,
    critical: bool = False,
) -> PipelineContext:
    """Install pip packages for the pyenv-managed Python.

    Args:
        context: The pipeline context
        timeout: Installation timeout in seconds (default: 600)
        critical: Whether failure should stop the pipeline (default: False)

    Returns:
        Updated pipeline context with installation results

    Raises:
        PipPackageInstallError: If installation fails and critical is True
    """
    from src.tasks.install_pip_packages import (
        PipPackageInstallError,
        get_installed_pip_packages,
        install_pip_packages,
    )

    logger = context.logger_instance

    # Check if Python feature is configured
    features = context.app_config.project.settings.system.packages.features
    if "python" not in features:
        logger.debug("Python feature not configured, skipping pip packages")
        context.results["pip_packages_installed"] = False
        context.results["pip_packages_skipped"] = True
        return context

    python_feature = features["python"]
    pip_packages = python_feature.pip_packages

    # Check if there are any pip packages to install
    if not pip_packages:
        logger.debug("No pip packages configured, skipping")
        context.results["pip_packages_installed"] = False
        context.results["pip_packages_skipped"] = True
        return context

    # Get pyenv directory
    pyenv_dir: Path = (
        context.app_config.project.paths.install.dependencies.pyenv.path
    )

    # Check if Python is installed
    if not context.results.get("python_installed", False):
        msg = "Python not installed, cannot install pip packages"
        logger.warning(msg)
        context.results["pip_packages_installed"] = False
        context.results["pip_packages_error"] = msg
        if critical:
            raise PipPackageInstallError(msg)
        return context

    # Check if packages are already installed
    installed_packages = get_installed_pip_packages(pyenv_dir)
    packages_to_install = [
        pkg for pkg in pip_packages if pkg not in installed_packages
    ]

    if not packages_to_install:
        logger.debug(
            f"All pip packages already installed: {', '.join(pip_packages)}"
        )
        context.results["pip_packages_installed"] = True
        context.results["pip_packages_already_present"] = True
        context.results["pip_packages_list"] = pip_packages
        return context

    # Perform installation
    try:
        logger.debug(
            f"Installing pip packages: {', '.join(packages_to_install)}"
        )
        install_pip_packages(
            pyenv_dir,
            packages=packages_to_install,
            upgrade=False,
            timeout=timeout,
        )

        packages_str = ", ".join(packages_to_install)
        logger.debug(f"Successfully installed pip packages: {packages_str}")

        context.results["pip_packages_installed"] = True
        context.results["pip_packages_list"] = pip_packages
        context.results["pip_packages_already_present"] = False

    except PipPackageInstallError as e:
        logger.error(f"Failed to install pip packages: {e.message}")
        context.errors.append(e)
        context.results["pip_packages_installed"] = False

        if critical:
            raise

    return context


def extract_wallpapers(context: PipelineContext) -> PipelineContext:
    """Extract wallpapers from the archive.

    Args:
        context: The pipeline context

    Returns:
        Updated pipeline context with extraction results
    """
    import tarfile

    logger: RichLogger = context.logger_instance
    wallpaper_dir: Path = (
        context.app_config.project.paths.install.dotfiles.wallpapers.path
    )
    wallpapers: Path = (
        context.app_config.project.paths.source.dotfiles.assets.wallpapers.file(
            "wallpapers.tar.gz"
        )
    )
    logger.debug(f"Extracting wallpapers to path: {wallpaper_dir}")
    logger.debug(f"Wallpapers archive path: {wallpapers}")
    try:
        with tarfile.open(wallpapers, "r:gz") as tar:
            tar.extractall(path=wallpaper_dir)
        logger.debug("Wallpapers extracted successfully")
        context.results["wallpapers_extracted"] = True
    except Exception as e:
        logger.error(f"Failed to extract wallpapers: {e}")
        context.errors.append(e)
        context.results["wallpapers_extracted"] = False
    return context


def install_component(
    context: PipelineContext,
    name: str,
    component: Literal["module", "tool"],
    install_path: Path,
    settings_overrides: dict[str, Any] | None = None,
) -> PipelineContext:
    """Install a module/tool with optional settings customization.

    This function:
    1. Copies the component from source to installation directory
    2. Applies settings overrides to config/settings.toml (if provided)
    3. Validates settings against Pydantic models (always enabled)
    4. Creates backups and supports rollback on failure

    Args:
        context: Pipeline context
        name: Component name (e.g., "hyprpaper-manager")
        component: Component type ("module" or "tool")
        install_path: Destination path for installation
        settings_overrides: Optional dict of settings to override
                          Uses dot notation for nested keys:
                          {
                              "hyprpaper.wallpaper_dirs": ["~/custom"],
                              "hyprpaper.max_preload_pool_mb": 200,
                          }

    Returns:
        Updated pipeline context with installation results

    Example:
        >>> install_component(
        ...     context=context,
        ...     name="hyprpaper-manager",
        ...     component="module",
        ...     install_path=Path("~/.local/share/dotfiles/modules/hyprpaper-manager"),
        ...     settings_overrides={
        ...         "hyprpaper.wallpaper_dirs": ["~/Pictures/wallpapers"],
        ...         "hyprpaper.max_preload_pool_mb": 200,
        ...     },
        ... )
    """
    import shutil

    component_type = f"{component}s"
    logger: RichLogger = context.logger_instance

    logger.debug(f"Installing {component}: {name}")

    try:
        # 1. Get source path
        module_path = context.app_config.project.paths.source.common[
            component_type
        ][name].path

        logger.debug(f"Source: {module_path}")
        logger.debug(f"Destination: {install_path}")

        # 2. Validate source exists
        if not module_path.exists():
            raise FileNotFoundError(
                f"Source {component} not found: {module_path}"
            )

        # 3. Copy component (ignore venv, cache, and build artifacts)
        logger.debug(f"Copying {component}...")

        def ignore_patterns(_directory, files):
            """Ignore virtual environments, cache, and build artifacts."""
            ignore = set()
            for f in files:
                if f in {
                    ".venv",
                    "venv",
                    "__pycache__",
                    ".pytest_cache",
                    ".mypy_cache",
                    ".ruff_cache",
                    "node_modules",
                    "dist",
                    "build",
                    "*.egg-info",
                }:
                    ignore.add(f)
            return ignore

        shutil.copytree(
            module_path,
            install_path,
            dirs_exist_ok=True,
            ignore=ignore_patterns,
        )
        logger.debug(f"{component.capitalize()} copied successfully")

        # 4. Apply settings overrides if provided
        if settings_overrides:
            logger.debug(
                f"Applying {len(settings_overrides)} settings overrides..."
            )

            settings_file = install_path / "config" / "settings.toml"

            if not settings_file.exists():
                logger.warning(
                    f"Settings file not found: {settings_file}. "
                    f"Skipping overrides."
                )
            else:
                # Get config model from registry for validation
                config_model = ConfigModelRegistry.get_model(name, component)

                if config_model:
                    logger.debug(
                        f"Using {config_model.__name__} for validation"
                    )
                else:
                    logger.warning(
                        f"No config model registered for '{name}'. "
                        f"Validation will be skipped."
                    )

                # Apply overrides with validation
                overrider = SettingsOverrider(logger=logger)

                result = overrider.apply_overrides(
                    settings_file=settings_file,
                    overrides=settings_overrides,
                    config_model=config_model,
                )

                if result.success:
                    logger.debug(
                        f"✓ Successfully applied {len(result.overrides_applied)} "
                        f"overrides"
                    )
                    context.results[f"{name}_settings_overridden"] = True
                    context.results[f"{name}_overrides"] = (
                        result.overrides_applied
                    )
                else:
                    logger.error(
                        f"✗ Failed to apply overrides: {'; '.join(result.errors)}"
                    )
                    context.results[f"{name}_settings_overridden"] = False
                    # Add errors but don't fail the installation
                    for error in result.errors:
                        context.errors.append(SettingsOverrideError(error))

        # 5. Mark installation as successful
        context.results[f"{name}_installed"] = True
        logger.debug(f"✓ Successfully installed {component}: {name}")

    except Exception as e:
        logger.error(f"✗ Failed to install {component} '{name}': {e}")
        context.errors.append(e)
        context.results[f"{name}_installed"] = False

    return context

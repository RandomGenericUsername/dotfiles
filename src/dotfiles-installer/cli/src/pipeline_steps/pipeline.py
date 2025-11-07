from pathlib import Path

from dotfiles_pipeline import PipelineStep
from dotfiles_pipeline.core.types import PipelineContext

from src.pipeline_steps.utils import (
    detect_and_initialize_package_manager,
    handle_previous_installation,
    install_packages,
    install_starship_prompt,
    update_system_packages,
)


class PrintInstallationMessageStep(PipelineStep):
    """Step to print installation start message."""

    @property
    def step_id(self) -> str:
        return "print_installation_message"

    @property
    def description(self) -> str:
        return "Print installation start message"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Print the installation message."""
        import subprocess

        install_root = context.app_config.project.paths.install.path
        subprocess.run(["clear"])
        context.logger_instance.panel(
            f"Starting installation in [bold green]"
            f"'{install_root}'[/bold green]"
        )
        return context


class CheckPreviousInstallStep(PipelineStep):
    """Step to check for previous installation."""

    @property
    def step_id(self) -> str:
        return "check_previous_install"

    @property
    def description(self) -> str:
        return "Check for previous installation"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Check for previous installation."""
        install_directory: Path = context.app_config.project.paths.install.path
        context.logger_instance.debug(
            f"Checking for previous installation at '{install_directory}'"
        )
        if not install_directory.exists():
            context.logger_instance.debug("No previous installation found")
            context.results["previous_install_found"] = False
            return context

        context.results["previous_install_found"] = True
        context.logger_instance.warning(
            f"Previous installation found at '{install_directory}'"
        )
        return context


class HandlePreviousInstallStep(PipelineStep):
    """Step to handle previous installation found."""

    @property
    def step_id(self) -> str:
        return "previous_install_found"

    @property
    def description(self) -> str:
        return "Previous installation found"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Handle previous installation found."""
        if not context.results.get("previous_install_found", False):
            return context

        return handle_previous_installation(context)


class DetectPackageManagerStep(PipelineStep):
    """Pipeline step to detect and initialize package manager."""

    @property
    def step_id(self) -> str:
        return "detect_package_manager"

    @property
    def description(self) -> str:
        return "Detect and initialize package manager"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Detect and initialize the package manager."""
        return detect_and_initialize_package_manager(context)


class UpdateSystemStep(PipelineStep):
    """Pipeline step to update system packages."""

    @property
    def step_id(self) -> str:
        return "update_system"

    @property
    def description(self) -> str:
        return "Update system packages"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Update system packages"""
        return update_system_packages(context)


class InstallPackagesStep(PipelineStep):
    """Pipeline step to install packages."""

    @property
    def step_id(self) -> str:
        return "install_packages"

    @property
    def description(self) -> str:
        return "Install system packages"

    @property
    def critical(self) -> bool:
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install the specified packages.

        Note: Assumes DetectPackageManagerStep has run successfully.
        Pipeline will have stopped if package manager detection failed.
        System update should be handled by UpdateSystemStep before this step.
        """
        return install_packages(context)


class InstallZshConfigStep(PipelineStep):
    """Pipeline step to install Zsh and Oh My Zsh."""

    @property
    def step_id(self) -> str:
        return "install_zsh"

    @property
    def description(self) -> str:
        return "Install Zsh and Oh My Zsh"

    @property
    def critical(self) -> bool:
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install Zsh and Oh My Zsh"""
        from src.pipeline_steps.utils import render_zsh_config

        return render_zsh_config(context)


class InstallOhMyZshStep(PipelineStep):
    """Pipeline step to install Oh My Zsh."""

    @property
    def step_id(self) -> str:
        return "install_oh_my_zsh"

    @property
    def description(self) -> str:
        return "Install Oh My Zsh framework"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 300.0

    @property
    def critical(self) -> bool:
        """Oh My Zsh installation is critical."""
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install Oh My Zsh."""
        from src.pipeline_steps.utils import install_oh_my_zsh_framework

        return install_oh_my_zsh_framework(context)


class InstallStarshipStep(PipelineStep):
    """Pipeline step to install Starship prompt."""

    @property
    def step_id(self) -> str:
        return "install_starship"

    @property
    def description(self) -> str:
        return "Install Starship prompt"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 300.0

    @property
    def critical(self) -> bool:
        return False

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install Starship prompt."""
        return install_starship_prompt(context)


class CreateDirectoriesStep(PipelineStep):
    """Step to create installation directories."""

    @property
    def step_id(self) -> str:
        return "create_directories"

    @property
    def description(self) -> str:
        return "Create installation directories"

    def run(self, context: PipelineContext) -> PipelineContext:
        """Create installation directories."""
        context.logger_instance.debug("Creating installation directories")
        try:
            # Create all registered directories at once
            context.app_config.project.paths.install.create()
            context.logger_instance.debug(
                "Installation directories created successfully"
            )
        except Exception as e:
            context.logger_instance.error(
                f"Failed to create installation directories: {e}"
            )
            context.errors.append(e)
        return context


class InstallNvmStep(PipelineStep):
    """Pipeline step to install NVM."""

    @property
    def step_id(self) -> str:
        return "install_nvm"

    @property
    def description(self) -> str:
        return "Install NVM (Node Version Manager)"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 300.0

    @property
    def critical(self) -> bool:
        """NVM installation is critical if the feature is enabled."""
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install NVM."""
        from src.pipeline_steps.utils import install_nvm_manager

        return install_nvm_manager(context)


class InstallNodejsStep(PipelineStep):
    """Pipeline step to install Node.js using NVM."""

    @property
    def step_id(self) -> str:
        return "install_nodejs"

    @property
    def description(self) -> str:
        return "Install Node.js runtime"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 600.0

    @property
    def critical(self) -> bool:
        """Node.js installation is critical if the feature is enabled."""
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install Node.js using NVM."""
        from src.pipeline_steps.utils import install_nodejs_runtime

        return install_nodejs_runtime(context)


class InstallPyenvStep(PipelineStep):
    """Pipeline step to install pyenv."""

    @property
    def step_id(self) -> str:
        return "install_pyenv"

    @property
    def description(self) -> str:
        return "Install pyenv (Python Version Manager)"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 300.0

    @property
    def critical(self) -> bool:
        """Pyenv installation is critical if the feature is enabled."""
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install pyenv."""
        from src.pipeline_steps.utils import install_pyenv_manager

        return install_pyenv_manager(context)


class InstallPythonStep(PipelineStep):
    """Pipeline step to install Python using pyenv."""

    @property
    def step_id(self) -> str:
        return "install_python"

    @property
    def description(self) -> str:
        return "Install Python runtime"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 600.0

    @property
    def critical(self) -> bool:
        """Python installation is critical if the feature is enabled."""
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install Python using pyenv."""
        from src.pipeline_steps.utils import install_python_runtime

        return install_python_runtime(context)


class InstallPipPackagesStep(PipelineStep):
    """Pipeline step to install pip packages for Python."""

    @property
    def step_id(self) -> str:
        return "install_pip_packages"

    @property
    def description(self) -> str:
        return "Install pip packages"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 600.0

    @property
    def critical(self) -> bool:
        """Pip package installation is not critical - allow pipeline to
        continue."""
        return False

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install pip packages for the pyenv-managed Python."""
        from src.pipeline_steps.utils import install_pip_packages_runtime

        return install_pip_packages_runtime(context)


class ExtractWallpapersStep(PipelineStep):
    """Pipeline step to extract wallpapers."""

    @property
    def step_id(self) -> str:
        return "extract_wallpapers"

    @property
    def description(self) -> str:
        return "Extract wallpapers"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 300.0

    @property
    def critical(self) -> bool:
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Extract wallpapers."""
        from src.pipeline_steps.utils import extract_wallpapers

        return extract_wallpapers(context)


class InstallModuleStep(PipelineStep):
    """Pipeline step to install hyprpaper."""

    def __init__(
        self,
        module_name: str,
        settings_overrides: dict[str, any] | None = None,
    ):
        self.module_name = module_name
        self.settings_overrides = settings_overrides

    @property
    def step_id(self) -> str:
        return "install_hyprpaper"

    @property
    def description(self) -> str:
        return "Install hyprpaper"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 300.0

    @property
    def critical(self) -> bool:
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install hyprpaper."""
        from src.pipeline_steps.utils import install_component

        return install_component(
            context=context,
            name=self.module_name,
            component="module",
            install_path=context.app_config.project.paths.install.modules[
                self.module_name
            ].path,
            settings_overrides=self.settings_overrides,
        )


class InstallToolStep(PipelineStep):
    """Pipeline step to install hyprpaper."""

    def __init__(
        self,
        tool_name: str,
        settings_overrides: dict[str, any] | None = None,
    ):
        self.tool_name = tool_name
        self.settings_overrides = settings_overrides

    @property
    def step_id(self) -> str:
        return "install_hyprpaper"

    @property
    def description(self) -> str:
        return "Install hyprpaper"

    @property
    def timeout(self) -> float | None:
        """Step timeout in seconds."""
        return 300.0

    @property
    def critical(self) -> bool:
        return True

    def run(self, context: PipelineContext) -> PipelineContext:
        """Install hyprpaper."""
        from src.pipeline_steps.utils import install_component

        return install_component(
            context=context,
            name=self.tool_name,
            component="tool",
            install_path=context.app_config.project.paths.install.tools[
                self.tool_name
            ].path,
            settings_overrides=self.settings_overrides,
        )

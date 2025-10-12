from src.config.enums import InstallType
from src.modules.pipeline import PipelineStep
from src.modules.pipeline.core.types import PipelineContext
from src.pipeline_steps.utils import (
    handle_clean_installation,
    handle_update_installation,
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
        context.logger_instance.info("Starting installation...")
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
        context.logger_instance.debug(
            f"Checking for previous installation at '{context.install_directory}'"
        )
        if not context.install_directory.exists():
            context.logger_instance.debug("No previous installation found")
            context.results["previous_install_found"] = False
            return context

        context.results["previous_install_found"] = True
        context.logger_instance.warning(
            f"Previous installation found at '{context.install_directory}'"
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

        install_type: InstallType = context.install_type

        try:
            match install_type:
                case InstallType.clean:
                    context = handle_clean_installation(context)
                case InstallType.update:
                    context = handle_update_installation(context)
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

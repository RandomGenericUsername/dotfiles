from pathlib import Path
from typing import Annotated

from dotfiles_logging import (
    ConsoleHandlers,
    Log,
    LogConfig,
    LogFormatters,
    LogFormatterStyleChoices,
    LogLevels,
    RichFeatureSettings,
    RichHandlerSettings,
    parse_log_level,
)
from dotfiles_logging.core.log_types import FileHandlerSpec
from dotfiles_logging.handlers.file import (
    FileHandlerSettings,
    FileHandlerTypes,
)
from dotfiles_logging.rich.rich_logger import RichLogger
from dotfiles_pipeline import Pipeline
from dotfiles_pipeline.core.types import PipelineContext, TaskStep
from src.config.config import AppConfig as PydanticAppConfig
from src.config.enums import InstallType
from src.config.settings import Settings
from src.pipeline_steps.pipeline import (
    CheckPreviousInstallStep,
    CreateDirectoriesStep,
    DetectPackageManagerStep,
    HandlePreviousInstallStep,
    InstallNodejsStep,
    InstallNvmStep,
    InstallOhMyZshStep,
    InstallPackagesStep,
    InstallPipPackagesStep,
    InstallPyenvStep,
    InstallPythonStep,
    InstallStarshipStep,
    InstallZshConfigStep,
    PrintInstallationMessageStep,
    UpdateSystemStep,
)
from typer import Option


def install(
    log_level_str: Annotated[
        str | None, Option("--log-level", "-l", help="Set logging level")
    ] = None,
    verbose: Annotated[
        int, Option("-v", count=True, help="Increase verbosity", min=0, max=3)
    ] = 0,
    install_directory: Annotated[
        Path | None,
        Option("--install-directory", "-i", help="Path to install dotfiles"),
    ] = None,
    backup_directory: Annotated[
        Path | None,
        Option("--backup-directory", "-b", help="Path to backup directory"),
    ] = None,
    install_type: Annotated[
        InstallType | None,
        Option("--install-type", "-t", help="Type of installation"),
    ] = None,
    hide: Annotated[
        bool | None, Option(help="Hide the installation directory")
    ] = None,
    log_to_file: Annotated[
        bool | None, Option(help="Output log to file")
    ] = None,
    log_directory: Annotated[
        Path | None,
        Option("--log-directory", "-L", help="Path to log directory"),
    ] = None,
) -> None:
    # Get default settings
    default_config = Settings.get()

    # Use provided values or fall back to defaults
    if install_directory is None:
        install_directory = default_config.cli_settings.installation_directory
    if backup_directory is None:
        backup_directory = default_config.cli_settings.backup_directory
    if install_type is None:
        install_type = default_config.cli_settings.install_type
    if hide is None:
        hide = default_config.cli_settings.hidden
    if log_to_file is None:
        log_to_file = default_config.cli_settings.debug.output_to_file
    if log_directory is None:
        log_directory = default_config.cli_settings.debug.log_directory

    if log_to_file and not log_directory.exists():
        try:
            log_directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create log directory {log_directory}: {e}"
            ) from e

    log_level: LogLevels = parse_log_level(
        log_level_str=log_level_str,
        verbosity=verbose,
        fallback=Settings.get().cli_settings.debug.log_level,
    )

    logger: RichLogger = Log.create_logger(
        config=LogConfig(
            name=__name__,
            log_level=log_level,
            formatter_style=LogFormatterStyleChoices.BRACE,
            formatter_type=LogFormatters.RICH,
            console_handler=ConsoleHandlers.RICH,
            handler_config=RichHandlerSettings(
                show_time=True,
                show_path=True,
                markup=True,
                rich_tracebacks=True,
            ),
            rich_features=RichFeatureSettings(
                enabled=True,
                table_show_lines=True,
                panel_box_style="rounded",
                panel_border_style="blue",
                progress_auto_refresh=True,
                status_spinner="dots",
            ),
            file_handlers=[
                FileHandlerSpec(
                    handler_type=FileHandlerTypes.FILE,
                    config=FileHandlerSettings(
                        filename=f"{log_directory}/install.log", mode="w"
                    ),
                )
            ],
        )
    )

    config: PydanticAppConfig = Settings.update(
        log_level_str=log_level_str,
        install_directory=install_directory,
        backup_directory=backup_directory,
        install_type=install_type,
        hide=hide,
        log_to_file=log_to_file,
        log_directory=log_directory,
    )

    context: PipelineContext[PydanticAppConfig] = PipelineContext(
        logger_instance=logger,
        app_config=config,
    )

    steps: list[TaskStep] = [
        PrintInstallationMessageStep(),
        CheckPreviousInstallStep(),
        HandlePreviousInstallStep(),
        CreateDirectoriesStep(),
        DetectPackageManagerStep(),
        UpdateSystemStep(),
        InstallPackagesStep(),
        InstallStarshipStep(),
        InstallZshConfigStep(),
        InstallOhMyZshStep(),
        InstallNvmStep(),
        InstallNodejsStep(),
        InstallPyenvStep(),
        InstallPythonStep(),
        InstallPipPackagesStep(),
    ]
    pipeline: Pipeline = Pipeline.create(steps)
    pipeline.run(context)

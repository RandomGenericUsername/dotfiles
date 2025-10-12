from pathlib import Path
from typing import Annotated

from typer import Option

from src.config.enums import InstallType
from src.config.settings import Settings
from src.modules.logging import (
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
from src.modules.logging.core.log_types import FileHandlerSpec
from src.modules.logging.handlers.file import (
    FileHandlerSettings,
    FileHandlerTypes,
)
from src.modules.logging.rich.rich_logger import RichLogger
from src.modules.pipeline import Pipeline
from src.modules.pipeline.core.types import PipelineContext, TaskStep
from src.pipeline_steps.pipeline import (
    CheckPreviousInstallStep,
    HandlePreviousInstallStep,
    PrintInstallationMessageStep,
)


def install(
    log_level_str: Annotated[
        str | None, Option("--log-level", "-l", help="Set logging level")
    ] = None,
    verbose: Annotated[
        int, Option("-v", count=True, help="Increase verbosity", min=0, max=3)
    ] = 0,
    install_directory: Annotated[
        Path,
        Option("--install-directory", "-i", help="Path to install dotfiles"),
    ] = Settings.install.directory,
    backup_directory: Annotated[
        Path,
        Option("--backup-directory", "-b", help="Path to backup directory"),
    ] = Settings.install.backup_directory,
    install_type: Annotated[
        InstallType,
        Option("--install-type", "-t", help="Type of installation"),
    ] = Settings.install.type,
    hide: Annotated[
        bool, Option(help="Hide the installation directory")
    ] = Settings.install.hidden,
    log_to_file: Annotated[
        bool, Option(help="Output log to file")
    ] = Settings.install.debug.output_to_file,
    log_directory: Annotated[
        Path, Option("--log-directory", "-L", help="Path to log directory")
    ] = Settings.install.debug.log_directory,
) -> None:

    if log_to_file and not log_directory.exists():
        message = (
            f"Log directory {log_directory} does not exist. "
            "Create it or specify an existing directory with '--log-directory'"
            " or disable logging to file with '--no-log-to-file'"
        )
        raise FileNotFoundError(message)

    log_level: LogLevels = parse_log_level(
        log_level_str=log_level_str,
        verbosity=verbose,
        fallback=Settings.install.debug.log_level,
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

    context: PipelineContext = PipelineContext(
        logger_instance=logger,
        install_directory=install_directory,
        backup_directory=backup_directory,
        install_type=install_type,
        dependencies_directory=install_directory / ".dependencies",
        scripts_directory=install_directory / ".scripts",
        config_directory=install_directory / "config",
    )

    steps: list[TaskStep] = [
        PrintInstallationMessageStep(),
        CheckPreviousInstallStep(),
        HandlePreviousInstallStep(),
    ]
    pipeline: Pipeline = Pipeline.create(steps)
    pipeline.run(context)

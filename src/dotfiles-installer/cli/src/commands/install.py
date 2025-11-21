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
from typer import Option

from src.config.config import AppConfig as PydanticAppConfig
from src.config.enums import InstallType
from src.config.settings import Settings
from src.pipeline_steps.pipeline import (
    CheckPreviousInstallStep,
    ConfigureDotfilesManagerStep,
    CreateDirectoriesStep,
    DetectPackageManagerStep,
    ExtractWallpapersStep,
    HandlePreviousInstallStep,
    InstallEwwConfigStep,
    InstallEwwStep,
    InstallModuleStep,
    InstallNodejsStep,
    InstallNvmStep,
    InstallOhMyZshStep,
    InstallPackagesStep,
    InstallPipPackagesStep,
    InstallPyenvStep,
    InstallPythonStep,
    InstallRofiConfigStep,
    InstallRustStep,
    InstallRustupStep,
    InstallStarshipStep,
    InstallToolStep,
    InstallWlogoutConfigStep,
    InstallZshConfigStep,
    PrintInstallationMessageStep,
    StartDaemonServiceStep,
    UpdateSystemStep,
)


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
    rebuild_containers: Annotated[
        bool | None,
        Option("--rebuild-containers", help="Force rebuild container images"),
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
    if rebuild_containers is None:
        rebuild_containers = default_config.cli_settings.rebuild_containers
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
        rebuild_containers=rebuild_containers,
        log_to_file=log_to_file,
        log_directory=log_directory,
    )

    context: PipelineContext[PydanticAppConfig] = PipelineContext(
        logger_instance=logger,
        app_config=config,
    )

    module_settings_overrides = {
        "hyprpaper-manager": {
            "hyprpaper.wallpaper_dirs": [
                str(context.app_config.project.paths.host["Wallpapers"])
            ],
            "hyprpaper.config_file": str(
                context.app_config.project.paths.install[
                    "dotfiles_config_hypr"
                ]
                / "hyprpaper.conf"
            ),
        },
        "colorscheme-orchestrator": {
            "orchestrator.default_output_dir": str(
                context.app_config.project.paths.install["dotfiles_cache"]
            ),
            "paths.colorscheme_generator_module": str(
                context.app_config.project.paths.install[
                    "dependencies_modules"
                ]
                / "colorscheme-generator"
            ),
        },
        "wallpaper-effects-orchestrator": {
            "logging.level": "DEBUG",
            "paths.modules_directory": str(
                context.app_config.project.paths.install[
                    "dependencies_modules"
                ]
            ),
        },
        "wallpaper-orchestrator": {
            "orchestrator.effects_output_dir": str(
                context.app_config.project.paths.install["dotfiles_cache"]
                / "wallpaper-effects"
            ),
            "orchestrator.colorscheme_output_dir": str(
                context.app_config.project.paths.install["dotfiles_cache"]
                / "colorscheme"
            ),
            "colorscheme.backend": "pywal",
            "hyprpaper.monitor": "all",
        },
        "rofi-wallpaper-selector": {
            "paths.wallpapers_dir": str(
                context.app_config.project.paths.install["dotfiles_wallpapers"]
            ),
            "paths.effects_cache_dir": str(
                context.app_config.project.paths.install["dotfiles_cache"]
                / "wallpaper-effects"
            ),
            "paths.dotfiles_manager_path": str(
                context.app_config.project.paths.install[
                    "dependencies_modules"
                ]
                / "manager"
            ),
        },
    }

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
        InstallWlogoutConfigStep(),
        InstallRustupStep(),
        InstallRustStep(),
        InstallEwwStep(),
        InstallEwwConfigStep(),
        InstallNvmStep(),
        InstallNodejsStep(),
        InstallPyenvStep(),
        InstallPythonStep(),
        InstallPipPackagesStep(),
        ExtractWallpapersStep(),
        InstallModuleStep(module_name="logging"),
        InstallModuleStep(module_name="pipeline"),
        InstallModuleStep(module_name="socket"),
        InstallModuleStep(
            module_name="event-protocol", run_makefile_install=True
        ),
        InstallModuleStep(module_name="daemon", run_makefile_install=True),
        InstallModuleStep(module_name="package-manager"),
        InstallModuleStep(module_name="container-manager"),
        InstallModuleStep(module_name="colorscheme-generator"),
        InstallModuleStep(module_name="state-manager"),
        InstallModuleStep(module_name="template-renderer"),
        InstallModuleStep(module_name="icon-generator"),
        InstallModuleStep(module_name="wallpaper-effects-processor"),
        InstallModuleStep(
            module_name="hyprpaper-manager",
            settings_overrides=module_settings_overrides["hyprpaper-manager"],
        ),
        InstallToolStep(
            tool_name="colorscheme-orchestrator",
            settings_overrides=module_settings_overrides[
                "colorscheme-orchestrator"
            ],
            run_makefile_install=True,
            timeout=60.0 * 5,
        ),
        InstallToolStep(
            tool_name="wallpaper-effects-orchestrator",
            settings_overrides=module_settings_overrides[
                "wallpaper-effects-orchestrator"
            ],
            run_makefile_install=True,
            timeout=60.0 * 5,
        ),
        InstallToolStep(
            tool_name="wallpaper-orchestrator",
            settings_overrides=module_settings_overrides[
                "wallpaper-orchestrator"
            ],
            run_makefile_install=True,
            timeout=60.0 * 5,
        ),
        InstallModuleStep(module_name="manager", run_makefile_install=True),
        InstallModuleStep(
            module_name="rofi-wallpaper-selector",
            settings_overrides=module_settings_overrides[
                "rofi-wallpaper-selector"
            ],
            run_makefile_install=True,
        ),
        InstallRofiConfigStep(),
        ConfigureDotfilesManagerStep(),
        StartDaemonServiceStep(),
    ]
    pipeline: Pipeline = Pipeline.create(steps)
    pipeline.run(context)

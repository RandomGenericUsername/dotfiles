from src.exceptions import InstallationConfirmationDeclinedException
from src.modules.pipeline import PipelineContext
from src.utils import file_manager


def backup_previous_installation(context: PipelineContext) -> PipelineContext:
    try:
        file_manager.copy_directory_filtered(
            src_path=context.install_directory,
            dest_path=context.backup_directory,
        )
        context.logger_instance.info(
            f"Previous installation backed up to {context.backup_directory}"
        )
    except Exception as e:
        context.logger_instance.error(
            f"Failed to backup previous installation: {e}"
        )
        context.errors.append(e)
    return context


def confirm_overwrite_previous_installation(context: PipelineContext) -> bool:
    confirmation_message = (
        f"[bold yellow]Overwrite previous installation at "
        f"[/bold yellow]'{context.install_directory}'?",
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


def handle_clean_installation(context: PipelineContext) -> PipelineContext:
    from src.utils import file_manager
    from src.utils.file_manager import has_any_contents, is_directory_empty

    context.logger_instance.info(
        f"Performing {context.install_type.value} installation"
    )
    if not is_directory_empty(
        context.install_directory
    ) and not confirm_overwrite_previous_installation(context):
        raise InstallationConfirmationDeclinedException(
            "User declined to overwrite previous installation"
        )

    if has_any_contents(context.install_directory) and confirm_backup(context):
        backup_previous_installation(context)

    # Delete the installation directory safely
    try:
        context.logger_instance.debug(
            f"Deleting installation directory: {context.install_directory}"
        )
        file_manager.delete_directory_safe(context.install_directory)
        context.logger_instance.debug(
            "Installation directory deleted successfully"
        )
    except Exception as e:
        context.logger_instance.error(
            f"Failed to delete installation directory: {e}"
        )
        context.errors.append(e)

    return context


def handle_update_installation(context: PipelineContext) -> PipelineContext:
    context.logger_instance.info(
        f"Performing {context.install_type.value} installation"
    )
    try:
        file_manager.delete_directory_safe(context.config_directory)
    except FileNotFoundError:
        pass
    except Exception as e:
        context.errors.append(e)

    try:
        file_manager.delete_directory_safe(context.dependencies_directory)
    except FileNotFoundError:
        pass
    except Exception as e:
        context.errors.append(e)

    return context

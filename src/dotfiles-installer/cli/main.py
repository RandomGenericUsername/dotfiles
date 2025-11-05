from pathlib import Path

from src.config.project_root import set_project_root

# Initialize project root BEFORE other imports that depend on it
set_project_root(Path(__file__).parent.parent.parent.parent)

# Now safe to import modules that use get_project_root()
from typer import Typer  # noqa: E402

from src.commands.install import install  # noqa: E402
from src.commands.uninstall import uninstall  # noqa: E402

cli = Typer()

# Register commands
cli.command(help="Install dotfiles")(install)
cli.command(help="Uninstall dotfiles")(uninstall)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

from pathlib import Path

from typer import Typer

from src.commands.install import install
from src.commands.uninstall import uninstall
from src.config.project_root import set_project_root

# Initialize project root at application startup
# main.py is at: src/dotfiles-installer/cli/main.py
# Go up 4 levels: cli -> dotfiles-installer -> src -> project_root
set_project_root(Path(__file__).parent.parent.parent.parent)

cli = Typer()

# Register commands
cli.command(help="Install dotfiles")(install)
cli.command(help="Uninstall dotfiles")(uninstall)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

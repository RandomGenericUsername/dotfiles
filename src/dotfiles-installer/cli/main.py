from typer import Typer

from src.commands.install import install
from src.commands.uninstall import uninstall

cli = Typer()

# Register commands
cli.command(help="Install dotfiles")(install)
cli.command(help="Uninstall dotfiles")(uninstall)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

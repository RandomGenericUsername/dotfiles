"""CLI entry point for minimal colorscheme viewer."""

import sys
from pathlib import Path

from rofi_colorscheme_viewer_minimal.viewer import MinimalViewer


def load_config() -> dict:
    """Load configuration from settings.toml."""
    import tomllib

    config_file = Path(__file__).parent.parent.parent / "config" / "settings.toml"

    with open(config_file, "rb") as f:
        return tomllib.load(f)


def main() -> None:
    """Main entry point."""
    try:
        config = load_config()

        viewer = MinimalViewer(
            colorscheme_file=config["paths"]["colorscheme_file"],
            swatch_dir=config["paths"]["swatch_dir"],
            swatch_size=config["display"]["swatch_size"],
            show_background=config["display"]["show_background"],
            show_foreground=config["display"]["show_foreground"],
            show_cursor=config["display"]["show_cursor"],
        )

        viewer.run()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

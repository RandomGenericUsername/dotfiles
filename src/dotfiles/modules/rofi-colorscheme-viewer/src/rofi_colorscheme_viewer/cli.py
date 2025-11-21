"""CLI interface for rofi-colorscheme-viewer."""

import os
import sys
from pathlib import Path

from rofi_colorscheme_viewer.config.config import load_config
from rofi_colorscheme_viewer.viewer.colorscheme_viewer import ColorschemeViewer


def main() -> None:
    """Display colorscheme colors in rofi.

    Called by rofi in script mode:
    - ROFI_RETV=0: List colors with format selector
    - ROFI_RETV=1: Handle selection (rofi passes selected item as argument)

    Examples:
        # List colors (called by rofi)
        $ ROFI_RETV=0 rofi-colorscheme-viewer

        # Handle selection (called by rofi)
        $ ROFI_RETV=1 rofi-colorscheme-viewer "Background #1a1b26"

        # Launch rofi with colorscheme viewer
        $ rofi -show colors -modi "colors:rofi-colorscheme-viewer"
    """
    # Parse config file from command line args if provided
    config_file = None
    if "--config" in sys.argv:
        idx = sys.argv.index("--config")
        if idx + 1 < len(sys.argv):
            config_file = Path(sys.argv[idx + 1])
    elif "-c" in sys.argv:
        idx = sys.argv.index("-c")
        if idx + 1 < len(sys.argv):
            config_file = Path(sys.argv[idx + 1])

    config = load_config(config_file)
    viewer = ColorschemeViewer(config)

    rofi_retv = os.environ.get("ROFI_RETV", "0")

    if rofi_retv == "0":
        # List mode - show menu
        viewer.show_menu()
    elif rofi_retv == "1":
        # Selection mode - handle selection
        # Rofi passes selected item as first argument
        # Get the first non-option argument
        selected_item = None
        for arg in sys.argv[1:]:
            if not arg.startswith("-") and arg not in [
                config_file,
                str(config_file),
            ]:
                selected_item = arg
                break

        if selected_item:
            viewer.handle_selection(selected_item)


if __name__ == "__main__":
    main()

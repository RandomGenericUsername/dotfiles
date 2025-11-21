"""Minimal colorscheme viewer for rofi."""

import json
import os
import subprocess
import sys
from pathlib import Path


class MinimalViewer:
    """Minimal colorscheme viewer with horizontal strip display."""

    def __init__(
        self,
        colorscheme_file: Path,
        swatch_dir: Path,
        swatch_size: int = 40,
        show_background: bool = True,
        show_foreground: bool = True,
        show_cursor: bool = True,
        clipboard_method: str = "wl-copy",
        auto_copy: bool = True,
    ):
        self.colorscheme_file = Path(colorscheme_file).expanduser()
        self.swatch_dir = Path(swatch_dir)
        self.swatch_size = swatch_size
        self.show_background = show_background
        self.show_foreground = show_foreground
        self.show_cursor = show_cursor
        self.clipboard_method = clipboard_method
        self.auto_copy = auto_copy

        # Ensure swatch directory exists
        self.swatch_dir.mkdir(parents=True, exist_ok=True)

    def load_colorscheme(self) -> dict:
        """Load the current colorscheme."""
        if not self.colorscheme_file.exists():
            raise FileNotFoundError(
                f"Colorscheme file not found: {self.colorscheme_file}"
            )

        with open(self.colorscheme_file) as f:
            return json.load(f)

    def generate_swatch(self, hex_color: str) -> Path:
        """Generate a color swatch using ImageMagick."""
        swatch_path = self.swatch_dir / f"{hex_color.lstrip('#')}.png"

        if not swatch_path.exists():
            subprocess.run(
                [
                    "convert",
                    "-size",
                    f"{self.swatch_size}x{self.swatch_size}",
                    f"xc:{hex_color}",
                    str(swatch_path),
                ],
                check=True,
                capture_output=True,
            )

        return swatch_path

    def get_colors(self, colorscheme: dict) -> list[tuple[str, str]]:
        """Get list of (name, hex) tuples for all colors to display."""
        colors = []
        color_dict = colorscheme.get("colors", {})

        # Only show the 16 main colors (no background/foreground/cursor)
        for i in range(16):
            hex_color = color_dict.get(f"color{i}", "#000000")
            colors.append((f"color{i}", hex_color))

        return colors

    def show_menu(self) -> None:
        """Display the color strip in rofi."""
        colorscheme = self.load_colorscheme()
        colors = self.get_colors(colorscheme)

        # Output each color as a rofi item with just the swatch icon
        for name, hex_color in colors:
            swatch_path = self.generate_swatch(hex_color)
            # Use hex color as the item text (hidden in icon-only mode)
            print(f"{hex_color}\x00icon\x1f{swatch_path}")
            sys.stdout.flush()

    def handle_selection(self, selected: str) -> None:
        """Handle color selection - copy hex to clipboard."""
        if not selected or not self.auto_copy:
            return

        # Copy to clipboard using configured method
        try:
            # Split the clipboard command to handle arguments
            # e.g., "xclip -selection clipboard" -> ["xclip", "-selection", "clipboard"]
            clipboard_cmd = self.clipboard_method.split()
            subprocess.run(
                clipboard_cmd,
                input=selected.encode(),
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Silently fail if clipboard tool is not available
            pass

    def run(self) -> None:
        """Run the viewer in rofi script mode."""
        # Check if we're in selection mode
        retv = os.environ.get("ROFI_RETV", "0")

        if retv == "0":
            # List mode - show the menu
            self.show_menu()
        elif retv == "1":
            # Selection mode - handle the selection
            selected = sys.argv[1] if len(sys.argv) > 1 else ""
            self.handle_selection(selected)

"""Colorscheme viewer for rofi."""

import json
import subprocess
import sys
from pathlib import Path

from rofi_colorscheme_viewer.config.config import AppConfig
from rofi_colorscheme_viewer.utils.format_converter import FormatConverter
from rofi_colorscheme_viewer.utils.rofi_formatter import RofiFormatter
from rofi_colorscheme_viewer.utils.swatch_generator import SwatchGenerator
from rofi_colorscheme_viewer.viewer.state_manager import StateManager


class ColorschemeViewer:
    """Rofi colorscheme viewer with format selection.

    This class handles displaying colorscheme colors in rofi with:
    - Format selector (hex, rgb, json) that cycles without closing rofi
    - Color swatches as icons
    - Metadata display in header
    - Copy to clipboard on selection

    Attributes:
        config: Application configuration
        state_manager: Format state manager
        swatch_generator: Color swatch generator
        formatter: Rofi output formatter
        converter: Format converter

    Example:
        >>> from rofi_colorscheme_viewer.config import load_config
        >>> config = load_config()
        >>> viewer = ColorschemeViewer(config)
        >>> viewer.show_menu()  # Called when ROFI_RETV=0
    """

    def __init__(self, config: AppConfig):
        """Initialize colorscheme viewer.

        Args:
            config: Application configuration
        """
        self.config = config

        # Initialize state manager
        state_file = config.paths.temp_dir / "format-state"
        self.state_manager = StateManager(
            state_file=state_file,
            available_formats=config.formats.available,
        )

        # Initialize swatch generator
        swatch_dir = config.paths.temp_dir / "swatches"
        self.swatch_generator = SwatchGenerator(
            swatch_size=config.rofi.swatch_size,
            output_dir=swatch_dir,
        )

        # Initialize utilities
        self.formatter = RofiFormatter()
        self.converter = FormatConverter()

    def load_colorscheme(self) -> dict:
        """Load colorscheme from JSON file.

        Returns:
            Colorscheme dictionary

        Raises:
            FileNotFoundError: If colorscheme file doesn't exist
            json.JSONDecodeError: If colorscheme file is invalid JSON

        Example:
            >>> scheme = viewer.load_colorscheme()
            >>> print(scheme["metadata"]["source_image"])
            '/home/user/wallpapers/mountain.png'
        """
        colorscheme_file = self.config.paths.colorscheme_file

        if not colorscheme_file.exists():
            raise FileNotFoundError(
                f"Colorscheme file not found: {colorscheme_file}"
            )

        with open(colorscheme_file) as f:
            return json.load(f)

    def get_color_entries(self) -> list[tuple[str, str, tuple[int, int, int]]]:
        """Get list of color entries from colorscheme.

        Returns:
            List of tuples: (friendly_name, hex_value, rgb_tuple)

        Example:
            >>> entries = viewer.get_color_entries()
            >>> entries[0]
            ('Background', '#1a1b26', (26, 27, 38))
        """
        scheme = self.load_colorscheme()

        entries = []

        # Special colors
        special = scheme.get("special", {})
        rgb_special = scheme.get("rgb", {})

        for name in ["background", "foreground", "cursor"]:
            if name in special:
                hex_value = special[name]
                rgb_value = tuple(rgb_special.get(name, [0, 0, 0]))
                friendly_name = name.capitalize()
                entries.append((friendly_name, hex_value, rgb_value))

        # Terminal colors (0-15)
        colors = scheme.get("colors", {})
        rgb_colors = scheme.get("rgb", {}).get("colors", [])

        for i in range(16):
            color_key = f"color{i}"
            if color_key in colors:
                hex_value = colors[color_key]
                rgb_value = (
                    tuple(rgb_colors[i]) if i < len(rgb_colors) else (0, 0, 0)
                )
                friendly_name = f"Color {i}"
                entries.append((friendly_name, hex_value, rgb_value))

        return entries

    def get_metadata_text(self) -> str:
        """Get metadata text for rofi header.

        Returns:
            Formatted metadata string

        Example:
            >>> viewer.get_metadata_text()
            'Source: mountain.png | Backend: pywal | Generated: 2024-01-15 14:30:22'
        """
        scheme = self.load_colorscheme()
        metadata = scheme.get("metadata", {})

        source = Path(metadata.get("source_image", "unknown")).name
        backend = metadata.get("backend", "unknown")
        generated = metadata.get("generated_at", "unknown")

        return (
            f"Source: {source} | Backend: {backend} | Generated: {generated}"
        )

    def get_format_selector_text(self) -> str:
        """Get format selector text based on current format.

        Returns:
            Format selector text with checkboxes

        Example:
            >>> viewer.get_format_selector_text()
            '🎨 Format: [✓] Hex  [ ] RGB  [ ] JSON'
        """
        current_format = self.state_manager.get_current_format()

        # Build checkbox text for each format
        checkboxes = []
        for fmt in self.config.formats.available:
            if fmt == current_format:
                checkboxes.append(f"[✓] {fmt.capitalize()}")
            else:
                checkboxes.append(f"[ ] {fmt.capitalize()}")

        return f"🎨 Format: {' '.join(checkboxes)}"

    def show_menu(
        self, highlight_index: int = 0, reload: bool = False
    ) -> None:
        """Show the rofi menu with colors and format selector.

        Args:
            highlight_index: Index of item to highlight (0 = format selector)
            reload: Whether to emit reload command (for format cycling)

        Example:
            >>> viewer.show_menu()  # Initial display
            >>> viewer.show_menu(highlight_index=0, reload=True)  # After format change
        """
        current_format = self.state_manager.get_current_format()

        # Emit metadata in header
        metadata_text = self.get_metadata_text()
        sys.stdout.write(self.formatter.message(metadata_text))

        # Emit selection state commands (for reload)
        if reload:
            sys.stdout.write(self.formatter.keep_selection())
            sys.stdout.write(self.formatter.new_selection(highlight_index))

        # Emit format selector
        format_text = self.get_format_selector_text()
        sys.stdout.write(self.formatter.item(format_text))

        # Emit color entries
        entries = self.get_color_entries()
        for name, hex_value, rgb_value in entries:
            # Generate swatch
            swatch_path = self.swatch_generator.generate(hex_value)

            # Format label based on current format
            formatted_value = self.converter.format_color(
                hex_value, rgb_value, current_format
            )
            label = f"{name:<12}  {formatted_value}"

            # Emit item with swatch icon
            sys.stdout.write(self.formatter.item(label, icon_path=swatch_path))

        # Emit reload command if needed
        if reload:
            sys.stdout.write(self.formatter.reload())

        sys.stdout.flush()

    def handle_selection(self, selected: str) -> None:
        """Handle user selection (Enter pressed on item).

        Args:
            selected: Selected item text from rofi

        Example:
            >>> viewer.handle_selection("🎨 Format: [✓] Hex  [ ] RGB  [ ] JSON")
            # Cycles format and reloads menu
            >>> viewer.handle_selection("Background      #1a1b26")
            # Copies #1a1b26 to clipboard
        """
        # Check if separator was selected - ignore
        if selected.startswith("─"):
            return

        # Check if format selector was clicked - cycle format and reload
        if selected.startswith("🎨 Format:"):
            self.state_manager.cycle_format()
            # Reload menu with format selector highlighted
            self.show_menu(highlight_index=0, reload=True)
            return

        # Color was selected - copy to clipboard
        current_format = self.state_manager.get_current_format()

        # Extract color value from selected line based on format
        if current_format == "hex":
            # Extract hex value (e.g., "#1a1b26")
            parts = selected.split()
            if len(parts) >= 2:
                value = parts[-1]  # Last part is the hex value
        elif current_format == "rgb":
            # Extract rgb value (e.g., "rgb(26, 27, 38)")
            if "rgb(" in selected:
                start = selected.index("rgb(")
                end = selected.index(")", start) + 1
                value = selected[start:end]
            else:
                return
        elif current_format == "json":
            # Extract JSON value
            if "{" in selected:
                start = selected.index("{")
                value = selected[start:]
            else:
                return
        else:
            return

        # Copy to clipboard using wl-copy
        try:
            subprocess.run(
                ["wl-copy"],
                input=value.encode(),
                check=True,
            )
        except subprocess.CalledProcessError:
            # Silently fail if wl-copy is not available
            pass

"""Rofi output formatter for script mode."""

from pathlib import Path
from typing import Optional


class RofiFormatter:
    """Formats output for rofi script mode.

    This class handles the special escape sequences and formatting
    required by rofi's script mode protocol.

    Rofi script mode uses null-separated key-value pairs:
    - \x00 (null byte) separates key from value
    - \x1f (unit separator) separates value from next key

    Example:
        >>> formatter = RofiFormatter()
        >>> formatter.message("Source: mountain.png")
        '\\x00message\\x1fSource: mountain.png\\n'
        >>> formatter.item("Background", icon_path="/tmp/swatch.png")
        'Background\\x00icon\\x1f/tmp/swatch.png\\n'
    """

    @staticmethod
    def message(text: str) -> str:
        """Format a message for rofi's message area (header).

        Args:
            text: Message text to display

        Returns:
            Formatted message string

        Example:
            >>> RofiFormatter.message("Source: mountain.png")
            '\\x00message\\x1fSource: mountain.png\\n'
        """
        return f"\x00message\x1f{text}\n"

    @staticmethod
    def item(label: str, icon_path: Optional[Path] = None) -> str:
        """Format an item for rofi's list.

        Args:
            label: Item label text
            icon_path: Optional path to icon image

        Returns:
            Formatted item string

        Example:
            >>> RofiFormatter.item("Background #1a1b26")
            'Background #1a1b26\\n'
            >>> RofiFormatter.item("Background", icon_path=Path("/tmp/swatch.png"))
            'Background\\x00icon\\x1f/tmp/swatch.png\\n'
        """
        if icon_path:
            return f"{label}\x00icon\x1f{icon_path}\n"
        return f"{label}\n"

    @staticmethod
    def keep_selection() -> str:
        """Format keep-selection command.

        Returns:
            Formatted keep-selection string

        Example:
            >>> RofiFormatter.keep_selection()
            '\\x00keep-selection\\x1ftrue\\n'
        """
        return "\x00keep-selection\x1ftrue\n"

    @staticmethod
    def new_selection(index: int) -> str:
        """Format new-selection command to highlight specific item.

        Args:
            index: Index of item to highlight (0-based)

        Returns:
            Formatted new-selection string

        Example:
            >>> RofiFormatter.new_selection(0)
            '\\x00new-selection\\x1f0\\n'
        """
        return f"\x00new-selection\x1f{index}\n"

    @staticmethod
    def reload() -> str:
        """Format reload command to refresh rofi without closing.

        Returns:
            Formatted reload string

        Example:
            >>> RofiFormatter.reload()
            '\\x00reload\\x1f1\\n'
        """
        return "\x00reload\x1f1\n"

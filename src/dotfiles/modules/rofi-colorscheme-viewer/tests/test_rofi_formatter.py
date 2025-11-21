"""Tests for rofi formatter utility."""

import pytest
from rofi_colorscheme_viewer.utils.rofi_formatter import RofiFormatter


class TestRofiFormatter:
    """Test rofi formatter."""

    @pytest.fixture
    def formatter(self):
        """Create a RofiFormatter instance."""
        return RofiFormatter()

    def test_item_with_icon(self, formatter):
        """Test formatting item with icon."""
        result = formatter.item("Background  #1a1b26", icon_path="/tmp/swatch.png")
        assert result == "Background  #1a1b26\x00icon\x1f/tmp/swatch.png\n"

    def test_item_without_icon(self, formatter):
        """Test formatting item without icon."""
        result = formatter.item("Background  #1a1b26")
        assert result == "Background  #1a1b26\n"

    def test_item_with_empty_label(self, formatter):
        """Test formatting with empty label."""
        result = formatter.item("", icon_path="/tmp/icon.png")
        assert result == "\x00icon\x1f/tmp/icon.png\n"

    def test_item_with_special_characters(self, formatter):
        """Test formatting with special characters in label."""
        result = formatter.item("Color 0  rgb(26, 27, 38)", icon_path="/tmp/icon.png")
        assert result == "Color 0  rgb(26, 27, 38)\x00icon\x1f/tmp/icon.png\n"

    def test_message(self, formatter):
        """Test formatting message."""
        result = formatter.message("Source: mountain.png | Backend: pywal")
        assert result == "\x00message\x1fSource: mountain.png | Backend: pywal\n"

    def test_message_with_empty_text(self, formatter):
        """Test formatting message with empty text."""
        result = formatter.message("")
        assert result == "\x00message\x1f\n"

    def test_keep_selection(self, formatter):
        """Test keep selection command."""
        result = formatter.keep_selection()
        assert result == "\x00keep-selection\x1ftrue\n"

    def test_new_selection(self, formatter):
        """Test new selection command."""
        result = formatter.new_selection(0)
        assert result == "\x00new-selection\x1f0\n"

        result = formatter.new_selection(5)
        assert result == "\x00new-selection\x1f5\n"

    def test_reload(self, formatter):
        """Test reload command."""
        result = formatter.reload()
        assert result == "\x00reload\x1f1\n"

    def test_multiple_items(self, formatter):
        """Test formatting multiple items."""
        items = [
            formatter.item("Item 1", icon_path="/tmp/icon1.png"),
            formatter.item("Item 2", icon_path="/tmp/icon2.png"),
            formatter.item("Item 3")
        ]

        assert len(items) == 3
        assert items[0] == "Item 1\x00icon\x1f/tmp/icon1.png\n"
        assert items[1] == "Item 2\x00icon\x1f/tmp/icon2.png\n"
        assert items[2] == "Item 3\n"

    def test_reload_sequence(self, formatter):
        """Test complete reload sequence."""
        sequence = [
            formatter.keep_selection(),
            formatter.new_selection(0),
            formatter.reload()
        ]

        assert sequence[0] == "\x00keep-selection\x1ftrue\n"
        assert sequence[1] == "\x00new-selection\x1f0\n"
        assert sequence[2] == "\x00reload\x1f1\n"

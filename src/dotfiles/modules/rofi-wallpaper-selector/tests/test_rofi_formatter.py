"""Tests for rofi formatter utility."""

import pytest
from rofi_wallpaper_selector.utils.rofi_formatter import format_rofi_item


class TestFormatRofiItem:
    """Test rofi item formatting."""

    def test_format_with_icon(self):
        """Test formatting item with icon."""
        result = format_rofi_item("wallpaper1", "/path/to/wallpaper1.png")
        assert result == "wallpaper1\x00icon\x1f/path/to/wallpaper1.png"

    def test_format_without_icon(self):
        """Test formatting item without icon."""
        result = format_rofi_item("off", None)
        assert result == "off"

    def test_format_with_empty_label(self):
        """Test formatting with empty label."""
        result = format_rofi_item("", "/path/to/icon.png")
        assert result == "\x00icon\x1f/path/to/icon.png"

    def test_format_with_special_characters(self):
        """Test formatting with special characters in label."""
        result = format_rofi_item("wall paper-1_test", "/path/to/icon.png")
        assert result == "wall paper-1_test\x00icon\x1f/path/to/icon.png"

"""Tests for format converter utility."""

import pytest
from rofi_colorscheme_viewer.utils.format_converter import FormatConverter


class TestFormatConverter:
    """Test format converter."""

    @pytest.fixture
    def converter(self):
        """Create a FormatConverter instance."""
        return FormatConverter()

    def test_format_hex(self, converter):
        """Test formatting color as hex."""
        result = converter.format_color("#1a1b26", (26, 27, 38), "hex")
        assert result == "#1a1b26"

    def test_format_rgb(self, converter):
        """Test formatting color as RGB."""
        result = converter.format_color("#1a1b26", (26, 27, 38), "rgb")
        assert result == "rgb(26, 27, 38)"

    def test_format_json(self, converter):
        """Test formatting color as JSON."""
        result = converter.format_color("#1a1b26", (26, 27, 38), "json")
        assert result == '{"r": 26, "g": 27, "b": 38}'

    def test_format_invalid_format(self, converter):
        """Test formatting with invalid format."""
        # Should default to hex
        result = converter.format_color("#1a1b26", (26, 27, 38), "invalid")
        assert result == "#1a1b26"

    def test_format_different_colors(self, converter):
        """Test formatting different colors."""
        # Red
        result = converter.format_color("#ff0000", (255, 0, 0), "rgb")
        assert result == "rgb(255, 0, 0)"

        # Green
        result = converter.format_color("#00ff00", (0, 255, 0), "rgb")
        assert result == "rgb(0, 255, 0)"

        # Blue
        result = converter.format_color("#0000ff", (0, 0, 255), "rgb")
        assert result == "rgb(0, 0, 255)"

    def test_format_all_formats(self, converter):
        """Test formatting same color in all formats."""
        hex_value = "#c0caf5"
        rgb_value = (192, 202, 245)

        hex_result = converter.format_color(hex_value, rgb_value, "hex")
        rgb_result = converter.format_color(hex_value, rgb_value, "rgb")
        json_result = converter.format_color(hex_value, rgb_value, "json")

        assert hex_result == "#c0caf5"
        assert rgb_result == "rgb(192, 202, 245)"
        assert json_result == '{"r": 192, "g": 202, "b": 245}'

    def test_format_case_insensitive(self, converter):
        """Test that format names are case-insensitive."""
        result_lower = converter.format_color("#1a1b26", (26, 27, 38), "hex")
        result_upper = converter.format_color("#1a1b26", (26, 27, 38), "HEX")
        result_mixed = converter.format_color("#1a1b26", (26, 27, 38), "Hex")

        assert result_lower == result_upper == result_mixed == "#1a1b26"

    def test_format_edge_cases(self, converter):
        """Test edge cases."""
        # Black
        result = converter.format_color("#000000", (0, 0, 0), "rgb")
        assert result == "rgb(0, 0, 0)"

        # White
        result = converter.format_color("#ffffff", (255, 255, 255), "rgb")
        assert result == "rgb(255, 255, 255)"

        # Gray
        result = converter.format_color("#808080", (128, 128, 128), "json")
        assert result == '{"r": 128, "g": 128, "b": 128}'

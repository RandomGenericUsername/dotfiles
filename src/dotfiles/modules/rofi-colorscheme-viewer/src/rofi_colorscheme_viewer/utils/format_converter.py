"""Format converter for color values."""

import json


class FormatConverter:
    """Converts color values between different formats.

    Supports conversion between:
    - Hex format: #1a1b26
    - RGB format: rgb(26, 27, 38)
    - JSON format: {"hex":"#1a1b26","rgb":[26,27,38]}

    Example:
        >>> converter = FormatConverter()
        >>> converter.to_hex("#1a1b26", (26, 27, 38))
        '#1a1b26'
        >>> converter.to_rgb("#1a1b26", (26, 27, 38))
        'rgb(26, 27, 38)'
        >>> converter.to_json("#1a1b26", (26, 27, 38))
        '{"hex":"#1a1b26","rgb":[26,27,38]}'
    """

    @staticmethod
    def to_hex(hex_value: str, rgb_value: tuple[int, int, int]) -> str:
        """Convert to hex format.

        Args:
            hex_value: Hex color code
            rgb_value: RGB tuple (not used, for consistency)

        Returns:
            Hex color code

        Example:
            >>> FormatConverter.to_hex("#1a1b26", (26, 27, 38))
            '#1a1b26'
        """
        return hex_value

    @staticmethod
    def to_rgb(hex_value: str, rgb_value: tuple[int, int, int]) -> str:
        """Convert to RGB format.

        Args:
            hex_value: Hex color code (not used, for consistency)
            rgb_value: RGB tuple

        Returns:
            RGB string in format: rgb(r, g, b)

        Example:
            >>> FormatConverter.to_rgb("#1a1b26", (26, 27, 38))
            'rgb(26, 27, 38)'
        """
        return f"rgb({rgb_value[0]}, {rgb_value[1]}, {rgb_value[2]})"

    @staticmethod
    def to_json(hex_value: str, rgb_value: tuple[int, int, int]) -> str:
        """Convert to JSON format.

        Args:
            hex_value: Hex color code
            rgb_value: RGB tuple

        Returns:
            JSON string with hex and rgb fields

        Example:
            >>> FormatConverter.to_json("#1a1b26", (26, 27, 38))
            '{"hex":"#1a1b26","rgb":[26,27,38]}'
        """
        return json.dumps(
            {"hex": hex_value, "rgb": list(rgb_value)}, separators=(",", ":")
        )

    @staticmethod
    def format_color(
        hex_value: str, rgb_value: tuple[int, int, int], format_type: str
    ) -> str:
        """Format color value based on format type.

        Args:
            hex_value: Hex color code
            rgb_value: RGB tuple
            format_type: Format type ("hex", "rgb", or "json")

        Returns:
            Formatted color string

        Raises:
            ValueError: If format_type is not supported

        Example:
            >>> FormatConverter.format_color("#1a1b26", (26, 27, 38), "hex")
            '#1a1b26'
            >>> FormatConverter.format_color("#1a1b26", (26, 27, 38), "rgb")
            'rgb(26, 27, 38)'
        """
        if format_type == "hex":
            return FormatConverter.to_hex(hex_value, rgb_value)
        elif format_type == "rgb":
            return FormatConverter.to_rgb(hex_value, rgb_value)
        elif format_type == "json":
            return FormatConverter.to_json(hex_value, rgb_value)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

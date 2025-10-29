"""Wallust backend for color scheme generation.

This backend uses wallust (Rust binary) to extract colors from images.
Wallust outputs JSON to stdout, which we parse.
"""

import json
import shutil
import subprocess
from pathlib import Path

from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.core.base import ColorSchemeGenerator
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
)
from colorscheme_generator.core.types import Color, ColorScheme, GeneratorConfig


class WallustGenerator(ColorSchemeGenerator):
    """Wallust backend for color extraction.
    
    Uses wallust (Rust binary) to generate colors. Wallust outputs JSON
    to stdout, which we parse directly without file I/O.
    
    Attributes:
        settings: Application configuration
        output_format: Output format for wallust (json or plain)
        backend_type: Wallust backend type (resized, full, thumb)
    """

    def __init__(self, settings: AppConfig):
        """Initialize WallustGenerator.
        
        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.output_format = settings.backends.wallust.output_format
        self.backend_type = settings.backends.wallust.backend_type

    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "wallust"

    def is_available(self) -> bool:
        """Check if wallust is available.
        
        Returns:
            True if wallust binary is in PATH
        """
        return shutil.which("wallust") is not None

    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
        """Generate color scheme using wallust.
        
        Args:
            image_path: Path to source image
            config: Runtime configuration
            
        Returns:
            ColorScheme object with extracted colors
            
        Raises:
            BackendNotAvailableError: If wallust is not available
            InvalidImageError: If image is invalid
            ColorExtractionError: If color extraction fails
        """
        # Ensure backend is available
        self.ensure_available()

        # Validate image
        image_path = image_path.expanduser().resolve()
        if not image_path.exists():
            raise InvalidImageError(image_path, "File does not exist")
        if not image_path.is_file():
            raise InvalidImageError(image_path, "Not a file")

        # Run wallust
        try:
            wallust_output = self._run_wallust(image_path, config)
        except Exception as e:
            raise ColorExtractionError(
                f"Failed to run wallust: {e}",
                backend=self.backend_name,
                image_path=image_path,
            ) from e

        # Parse JSON output
        try:
            wallust_colors = json.loads(wallust_output)
        except json.JSONDecodeError as e:
            raise ColorExtractionError(
                f"Failed to parse wallust JSON output: {e}",
                backend=self.backend_name,
                image_path=image_path,
            ) from e

        # Convert to ColorScheme
        return self._parse_wallust_output(wallust_colors, image_path)

    def _run_wallust(self, image_path: Path, config: GeneratorConfig) -> str:
        """Run wallust command and return JSON output.
        
        Args:
            image_path: Path to source image
            config: Runtime configuration
            
        Returns:
            JSON output from wallust
        """
        cmd = [
            "wallust",
            "run",
            str(image_path),
            "--backend", self.backend_type,
            "--json",  # Output JSON to stdout
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise ColorExtractionError(
                f"Wallust command failed: {e.stderr}",
                backend=self.backend_name,
                image_path=image_path,
            ) from e
        except FileNotFoundError as e:
            raise BackendNotAvailableError(
                self.backend_name,
                "wallust command not found. Install with: cargo install wallust",
            ) from e

    def _parse_wallust_output(
        self, wallust_colors: dict, image_path: Path
    ) -> ColorScheme:
        """Parse wallust JSON output into ColorScheme.
        
        Args:
            wallust_colors: Wallust colors dict from JSON output
            image_path: Source image path
            
        Returns:
            ColorScheme object
        """
        # Wallust format (similar to pywal):
        # {
        #   "special": {"background": "#...", "foreground": "#...", "cursor": "#..."},
        #   "colors": {"color0": "#...", "color1": "#...", ...}
        # }
        
        special = wallust_colors.get("special", {})
        colors_dict = wallust_colors.get("colors", {})

        # Extract special colors
        background = self._parse_color(special.get("background", "#000000"))
        foreground = self._parse_color(special.get("foreground", "#ffffff"))
        cursor = self._parse_color(special.get("cursor", foreground.hex))

        # Extract terminal colors (0-15)
        colors = []
        for i in range(16):
            color_key = f"color{i}"
            if color_key in colors_dict:
                colors.append(self._parse_color(colors_dict[color_key]))
            else:
                # Fallback if color missing
                colors.append(Color(hex="#000000", rgb=(0, 0, 0)))

        return ColorScheme(
            background=background,
            foreground=foreground,
            cursor=cursor,
            colors=colors,
            source_image=str(image_path),
            backend=self.backend_name,
        )

    def _parse_color(self, hex_color: str) -> Color:
        """Parse hex color string to Color object.
        
        Args:
            hex_color: Hex color string (e.g., "#1a1a1a")
            
        Returns:
            Color object
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip("#")
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return Color(hex=f"#{hex_color}", rgb=(r, g, b))


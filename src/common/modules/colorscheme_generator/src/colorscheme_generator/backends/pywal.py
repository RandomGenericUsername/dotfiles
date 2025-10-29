"""Pywal backend for color scheme generation.

This backend uses pywal (Python library or CLI) to extract colors from images.
Pywal always writes to ~/.cache/wal/, which we read from.
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


class PywalGenerator(ColorSchemeGenerator):
    """Pywal backend for color extraction.
    
    Uses pywal to generate colors. Pywal writes to a fixed location
    (~/.cache/wal/), which we read from to extract the ColorScheme.
    
    Attributes:
        settings: Application configuration
        cache_dir: Directory where pywal writes its output
        use_library: Whether to use pywal as library vs CLI
    """

    def __init__(self, settings: AppConfig):
        """Initialize PywalGenerator.
        
        Args:
            settings: Application configuration
        """
        self.settings = settings
        self.cache_dir = Path(settings.backends.pywal.cache_dir).expanduser()
        self.use_library = settings.backends.pywal.use_library

    @property
    def backend_name(self) -> str:
        """Get backend name."""
        return "pywal"

    def is_available(self) -> bool:
        """Check if pywal is available.
        
        Returns:
            True if pywal is available (library or CLI)
        """
        if self.use_library:
            try:
                import pywal  # noqa: F401
                return True
            except ImportError:
                return False
        else:
            return shutil.which("wal") is not None

    def generate(self, image_path: Path, config: GeneratorConfig) -> ColorScheme:
        """Generate color scheme using pywal.
        
        Args:
            image_path: Path to source image
            config: Runtime configuration
            
        Returns:
            ColorScheme object with extracted colors
            
        Raises:
            BackendNotAvailableError: If pywal is not available
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

        # Run pywal
        try:
            if self.use_library:
                self._run_pywal_library(image_path, config)
            else:
                self._run_pywal_cli(image_path, config)
        except Exception as e:
            raise ColorExtractionError(
                f"Failed to run pywal: {e}",
                backend=self.backend_name,
                image_path=image_path,
            ) from e

        # Read colors from pywal's output
        colors_file = self.cache_dir / "colors.json"
        if not colors_file.exists():
            raise ColorExtractionError(
                f"Pywal output file not found: {colors_file}",
                backend=self.backend_name,
                image_path=image_path,
            )

        try:
            with open(colors_file) as f:
                pywal_colors = json.load(f)
        except Exception as e:
            raise ColorExtractionError(
                f"Failed to read pywal output: {e}",
                backend=self.backend_name,
                image_path=image_path,
            ) from e

        # Convert to ColorScheme
        return self._parse_pywal_output(pywal_colors, image_path)

    def _run_pywal_library(self, image_path: Path, config: GeneratorConfig) -> None:
        """Run pywal as Python library.
        
        Args:
            image_path: Path to source image
            config: Runtime configuration
        """
        try:
            import pywal
            from pywal import colors as pywal_colors
            from pywal import image as pywal_image
        except ImportError as e:
            raise BackendNotAvailableError(
                self.backend_name,
                "pywal library not installed. Install with: pip install pywal",
            ) from e

        # Generate colors using pywal
        img = pywal_image.get(str(image_path))
        palette = pywal_image.colors(img, backend="wal")
        
        # Write to cache directory
        pywal_colors.file(palette, self.cache_dir)

    def _run_pywal_cli(self, image_path: Path, config: GeneratorConfig) -> None:
        """Run pywal as CLI command.
        
        Args:
            image_path: Path to source image
            config: Runtime configuration
        """
        cmd = ["wal", "-i", str(image_path), "-n"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise ColorExtractionError(
                f"Pywal command failed: {e.stderr}",
                backend=self.backend_name,
                image_path=image_path,
            ) from e
        except FileNotFoundError as e:
            raise BackendNotAvailableError(
                self.backend_name,
                "wal command not found. Install pywal.",
            ) from e

    def _parse_pywal_output(
        self, pywal_colors: dict, image_path: Path
    ) -> ColorScheme:
        """Parse pywal JSON output into ColorScheme.
        
        Args:
            pywal_colors: Pywal colors dict from colors.json
            image_path: Source image path
            
        Returns:
            ColorScheme object
        """
        # Pywal format:
        # {
        #   "special": {"background": "#...", "foreground": "#...", "cursor": "#..."},
        #   "colors": {"color0": "#...", "color1": "#...", ...}
        # }
        
        special = pywal_colors.get("special", {})
        colors_dict = pywal_colors.get("colors", {})

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


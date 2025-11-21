"""Color swatch generator using ImageMagick."""

import subprocess
from pathlib import Path


class SwatchGenerator:
    """Generates color swatches as PNG images using ImageMagick.

    This class creates square PNG images filled with a solid color,
    used as icons in rofi to display color swatches.

    Attributes:
        swatch_size: Size of the swatch in pixels (width and height)
        output_dir: Directory to store generated swatches

    Example:
        >>> generator = SwatchGenerator(size=100, output_dir=Path("/tmp/swatches"))
        >>> swatch_path = generator.generate("#1a1b26")
        >>> print(swatch_path)
        PosixPath('/tmp/swatches/1a1b26.png')
    """

    def __init__(self, swatch_size: int, output_dir: Path):
        """Initialize swatch generator.

        Args:
            swatch_size: Size of the swatch in pixels
            output_dir: Directory to store generated swatches
        """
        self.swatch_size = swatch_size
        self.output_dir = output_dir

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, hex_color: str) -> Path:
        """Generate a color swatch PNG.

        Args:
            hex_color: Hex color code (with or without #)

        Returns:
            Path to the generated swatch PNG

        Raises:
            subprocess.CalledProcessError: If ImageMagick convert fails

        Example:
            >>> swatch_path = generator.generate("#1a1b26")
            >>> swatch_path.exists()
            True
        """
        # Remove # from hex color for filename
        clean_hex = hex_color.lstrip("#")

        # Output path
        output_path = self.output_dir / f"{clean_hex}.png"

        # Skip if already exists
        if output_path.exists():
            return output_path

        # Generate swatch using ImageMagick
        subprocess.run(
            [
                "convert",
                "-size",
                f"{self.swatch_size}x{self.swatch_size}",
                f"xc:{hex_color}",
                str(output_path),
            ],
            check=True,
            capture_output=True,
        )

        return output_path

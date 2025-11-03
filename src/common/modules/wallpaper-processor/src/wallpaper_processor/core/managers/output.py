"""Output manager for saving processed images."""

from pathlib import Path

from PIL import Image
from wallpaper_processor.config.enums import OutputFormat
from wallpaper_processor.core.exceptions import UnsupportedFormatError


class OutputManager:
    """Manages output image saving."""

    SUPPORTED_FORMATS = {
        OutputFormat.PNG,
        OutputFormat.JPEG,
        OutputFormat.JPG,
        OutputFormat.WEBP,
        OutputFormat.BMP,
        OutputFormat.TIFF,
    }

    @staticmethod
    def save_image(
        image: Image.Image,
        output_path: Path,
        output_format: OutputFormat | None = None,
        quality: int = 95,
    ) -> Path:
        """Save image to file.

        Args:
            image: PIL Image to save
            output_path: Output file path
            output_format: Output format (inferred from path if None)
            quality: Quality for lossy formats (1-100)

        Returns:
            Path to saved file

        Raises:
            UnsupportedFormatError: If format is not supported
        """
        # Determine format
        if output_format is None:
            # Infer from file extension
            ext = output_path.suffix.lstrip(".").lower()
            try:
                output_format = OutputFormat(ext)
            except ValueError as err:
                raise UnsupportedFormatError(ext) from err

        # Validate format
        if output_format not in OutputManager.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(output_format.value)

        # Prepare save kwargs
        save_kwargs = {}
        if output_format in (
            OutputFormat.JPEG,
            OutputFormat.JPG,
            OutputFormat.WEBP,
        ):
            save_kwargs["quality"] = quality

        # Save image
        image.save(output_path, **save_kwargs)

        return output_path

    @staticmethod
    def is_format_supported(format_name: str) -> bool:
        """Check if format is supported.

        Args:
            format_name: Format name (e.g., "png", "jpeg")

        Returns:
            True if supported, False otherwise
        """
        try:
            fmt = OutputFormat(format_name.lower())
            return fmt in OutputManager.SUPPORTED_FORMATS
        except ValueError:
            return False

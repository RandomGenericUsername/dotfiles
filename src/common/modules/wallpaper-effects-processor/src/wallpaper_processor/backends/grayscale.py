"""Grayscale effect implementations (ImageMagick and PIL)."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import ProcessingError
from wallpaper_processor.core.registry import register_effect
from wallpaper_processor.core.types import EffectParams, GrayscaleParams


@register_effect("grayscale")
class ImageMagickGrayscale(WallpaperEffect):
    """Grayscale effect using ImageMagick."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "grayscale"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "imagemagick"

    def is_available(self) -> bool:
        """Check if ImageMagick is available."""
        return shutil.which("convert") is not None

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return GrayscaleParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply grayscale conversion using ImageMagick.

        Args:
            image: PIL Image object
            params: GrayscaleParams instance

        Returns:
            Grayscale PIL Image object

        Raises:
            ProcessingError: If ImageMagick command fails
        """
        if not isinstance(params, GrayscaleParams):
            raise TypeError(f"Expected GrayscaleParams, got {type(params)}")

        # Create temporary files
        with (
            tempfile.NamedTemporaryFile(
                suffix=".png", delete=False
            ) as input_tmp,
            tempfile.NamedTemporaryFile(
                suffix=".png", delete=False
            ) as output_tmp,
        ):
            input_path = Path(input_tmp.name)
            output_path = Path(output_tmp.name)

        try:
            # Save input image
            image.save(input_path)

            # Build ImageMagick command based on method
            if params.method == "average":
                cmd = [
                    "convert",
                    str(input_path),
                    "-grayscale",
                    "Average",
                    str(output_path),
                ]
            elif params.method == "luminosity":
                cmd = [
                    "convert",
                    str(input_path),
                    "-grayscale",
                    "Rec709Luminance",
                    str(output_path),
                ]
            else:  # mean
                cmd = [
                    "convert",
                    str(input_path),
                    "-set",
                    "colorspace",
                    "Gray",
                    "-separate",
                    "-evaluate-sequence",
                    "Mean",
                    str(output_path),
                ]

            # Run ImageMagick
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                raise ProcessingError(
                    f"ImageMagick grayscale failed: {result.stderr}"
                )

            # Load result
            grayscale_image = Image.open(output_path)
            # Convert to RGB mode to maintain consistency with PIL backend
            # and avoid colorspace issues when saving/displaying
            result_image = grayscale_image.convert("RGB")
            grayscale_image.close()

            return result_image

        finally:
            # Clean up temp files
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


@register_effect("grayscale")
class PILGrayscale(WallpaperEffect):
    """Grayscale effect using PIL (fallback)."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "grayscale"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "pil"

    def is_available(self) -> bool:
        """PIL is always available."""
        return True

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return GrayscaleParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply grayscale conversion using PIL.

        Args:
            image: PIL Image object
            params: GrayscaleParams instance

        Returns:
            Grayscale PIL Image object
        """
        if not isinstance(params, GrayscaleParams):
            raise TypeError(f"Expected GrayscaleParams, got {type(params)}")

        # PIL's convert to 'L' mode uses luminosity method
        # Convert to grayscale and back to RGB to maintain mode
        grayscale = ImageOps.grayscale(image)
        return grayscale.convert("RGB")

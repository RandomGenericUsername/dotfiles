"""Color overlay effect implementations (ImageMagick and PIL)."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import ProcessingError
from wallpaper_processor.core.types import ColorOverlayParams, EffectParams


class ImageMagickColorOverlay(WallpaperEffect):
    """Color overlay effect using ImageMagick."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "color_overlay"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "imagemagick"

    def is_available(self) -> bool:
        """Check if ImageMagick is available."""
        return shutil.which("convert") is not None

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return ColorOverlayParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply color overlay using ImageMagick.

        Args:
            image: PIL Image object
            params: ColorOverlayParams instance

        Returns:
            Color-overlaid PIL Image object

        Raises:
            ProcessingError: If ImageMagick command fails
        """
        if not isinstance(params, ColorOverlayParams):
            raise TypeError(f"Expected ColorOverlayParams, got {type(params)}")

        # Create temporary files
        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as input_tmp, tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ) as output_tmp:
            input_path = Path(input_tmp.name)
            output_path = Path(output_tmp.name)

        try:
            # Save input image
            image.save(input_path)

            # Convert opacity to percentage for ImageMagick
            opacity_percent = int(params.opacity * 100)

            # ImageMagick command to overlay color
            cmd = [
                "convert",
                str(input_path),
                "(",
                "-clone",
                "0",
                "-fill",
                params.color,
                "-colorize",
                "100",
                ")",
                "-compose",
                "blend",
                "-define",
                f"compose:args={opacity_percent}",
                "-composite",
                str(output_path),
            ]

            # Run ImageMagick
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                raise ProcessingError(
                    f"ImageMagick color overlay failed: {result.stderr}"
                )

            # Load result
            overlaid_image = Image.open(output_path)
            result_image = overlaid_image.copy()
            overlaid_image.close()

            return result_image

        finally:
            # Clean up temp files
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


class PILColorOverlay(WallpaperEffect):
    """Color overlay effect using PIL (fallback)."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "color_overlay"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "pil"

    def is_available(self) -> bool:
        """PIL is always available."""
        return True

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return ColorOverlayParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply color overlay using PIL.

        Args:
            image: PIL Image object
            params: ColorOverlayParams instance

        Returns:
            Color-overlaid PIL Image object
        """
        if not isinstance(params, ColorOverlayParams):
            raise TypeError(f"Expected ColorOverlayParams, got {type(params)}")

        # Convert hex color to RGB
        color_hex = params.color.lstrip("#")
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)

        # Create color overlay
        overlay = Image.new("RGB", image.size, (r, g, b))

        # Blend with original image
        # PIL blend: result = image1 * (1 - alpha) + image2 * alpha
        # We want: result = original * (1 - opacity) + overlay * opacity
        result = Image.blend(image.convert("RGB"), overlay, params.opacity)

        return result


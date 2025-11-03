"""Blur effect implementations (ImageMagick and PIL)."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter

from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import ProcessingError
from wallpaper_processor.core.types import BlurParams, EffectParams


class ImageMagickBlur(WallpaperEffect):
    """Blur effect using ImageMagick."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "blur"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "imagemagick"

    def is_available(self) -> bool:
        """Check if ImageMagick is available."""
        return shutil.which("convert") is not None

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return BlurParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply blur using ImageMagick.

        Args:
            image: PIL Image object
            params: BlurParams instance

        Returns:
            Blurred PIL Image object

        Raises:
            ProcessingError: If ImageMagick command fails
        """
        if not isinstance(params, BlurParams):
            raise TypeError(f"Expected BlurParams, got {type(params)}")

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

            # Build ImageMagick command
            # -blur radiusxsigma
            blur_arg = f"{params.radius}x{params.sigma}"
            cmd = [
                "convert",
                str(input_path),
                "-blur",
                blur_arg,
                str(output_path),
            ]

            # Run ImageMagick
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                raise ProcessingError(
                    f"ImageMagick blur failed: {result.stderr}"
                )

            # Load result
            blurred_image = Image.open(output_path)
            # Copy to ensure we can delete temp file
            result_image = blurred_image.copy()
            blurred_image.close()

            return result_image

        finally:
            # Clean up temp files
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


class PILBlur(WallpaperEffect):
    """Blur effect using PIL (fallback)."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "blur"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "pil"

    def is_available(self) -> bool:
        """PIL is always available."""
        return True

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return BlurParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply blur using PIL.

        Args:
            image: PIL Image object
            params: BlurParams instance

        Returns:
            Blurred PIL Image object
        """
        if not isinstance(params, BlurParams):
            raise TypeError(f"Expected BlurParams, got {type(params)}")

        # PIL's GaussianBlur uses radius parameter
        # We use sigma as the radius for consistency
        return image.filter(ImageFilter.GaussianBlur(radius=params.sigma))

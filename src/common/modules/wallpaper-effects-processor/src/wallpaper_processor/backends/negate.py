"""Negate (color inversion) effect implementations (ImageMagick and PIL)."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import ProcessingError
from wallpaper_processor.core.registry import register_effect
from wallpaper_processor.core.types import EffectParams, NegateParams


@register_effect("negate")
class ImageMagickNegate(WallpaperEffect):
    """Negate effect using ImageMagick."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "negate"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "imagemagick"

    def is_available(self) -> bool:
        """Check if ImageMagick is available."""
        return shutil.which("convert") is not None

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return NegateParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply color inversion using ImageMagick.

        Args:
            image: PIL Image object
            params: NegateParams instance

        Returns:
            Color-inverted PIL Image object

        Raises:
            ProcessingError: If ImageMagick command fails
        """
        if not isinstance(params, NegateParams):
            raise TypeError(f"Expected NegateParams, got {type(params)}")

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

            # Build ImageMagick command
            # -channel RGB -negate +channel inverts RGB channels only
            cmd = [
                "convert",
                str(input_path),
                "-channel",
                "RGB",
                "-negate",
                "+channel",
                str(output_path),
            ]

            # Run ImageMagick
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                raise ProcessingError(
                    f"ImageMagick negate failed: {result.stderr}"
                )

            # Load result
            negated_image = Image.open(output_path)
            result_image = negated_image.copy()
            negated_image.close()

            return result_image

        finally:
            # Clean up temp files
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


@register_effect("negate")
class PILNegate(WallpaperEffect):
    """Negate effect using PIL (fallback)."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "negate"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "pil"

    def is_available(self) -> bool:
        """PIL is always available."""
        return True

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return NegateParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply color inversion using PIL.

        Args:
            image: PIL Image object
            params: NegateParams instance

        Returns:
            Color-inverted PIL Image object
        """
        if not isinstance(params, NegateParams):
            raise TypeError(f"Expected NegateParams, got {type(params)}")

        # PIL's invert function inverts all channels
        return ImageOps.invert(image.convert("RGB"))

"""Saturation effect implementations (ImageMagick and PIL)."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance

from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import ProcessingError
from wallpaper_processor.core.types import EffectParams, SaturationParams


class ImageMagickSaturation(WallpaperEffect):
    """Saturation effect using ImageMagick."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "saturation"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "imagemagick"

    def is_available(self) -> bool:
        """Check if ImageMagick is available."""
        return shutil.which("convert") is not None

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return SaturationParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply saturation adjustment using ImageMagick.

        Args:
            image: PIL Image object
            params: SaturationParams instance

        Returns:
            Saturation-adjusted PIL Image object

        Raises:
            ProcessingError: If ImageMagick command fails
        """
        if not isinstance(params, SaturationParams):
            raise TypeError(f"Expected SaturationParams, got {type(params)}")

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

            # Convert adjustment percentage to ImageMagick modulate value
            # modulate saturation: 0 = grayscale, 100 = original, 200 = double
            saturation_value = 100 + params.adjustment
            cmd = [
                "convert",
                str(input_path),
                "-modulate",
                f"100,{saturation_value},100",
                str(output_path),
            ]

            # Run ImageMagick
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                raise ProcessingError(
                    f"ImageMagick saturation failed: {result.stderr}"
                )

            # Load result
            adjusted_image = Image.open(output_path)
            result_image = adjusted_image.copy()
            adjusted_image.close()

            return result_image

        finally:
            # Clean up temp files
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


class PILSaturation(WallpaperEffect):
    """Saturation effect using PIL (fallback)."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "saturation"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "pil"

    def is_available(self) -> bool:
        """PIL is always available."""
        return True

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return SaturationParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply saturation adjustment using PIL.

        Args:
            image: PIL Image object
            params: SaturationParams instance

        Returns:
            Saturation-adjusted PIL Image object
        """
        if not isinstance(params, SaturationParams):
            raise TypeError(f"Expected SaturationParams, got {type(params)}")

        # Convert adjustment percentage to PIL enhancement factor
        # -100 = 0.0 (grayscale), 0 = 1.0 (original),
        # 100 = 2.0 (double saturation)
        factor = 1.0 + (params.adjustment / 100.0)
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)

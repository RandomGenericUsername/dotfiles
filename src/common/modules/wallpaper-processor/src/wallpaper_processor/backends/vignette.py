"""Vignette effect implementations (ImageMagick and PIL)."""

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import ProcessingError
from wallpaper_processor.core.types import EffectParams, VignetteParams


class ImageMagickVignette(WallpaperEffect):
    """Vignette effect using ImageMagick."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "vignette"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "imagemagick"

    def is_available(self) -> bool:
        """Check if ImageMagick is available."""
        return shutil.which("convert") is not None

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return VignetteParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply vignette using ImageMagick.

        Args:
            image: PIL Image object
            params: VignetteParams instance

        Returns:
            Vignetted PIL Image object

        Raises:
            ProcessingError: If ImageMagick command fails
        """
        if not isinstance(params, VignetteParams):
            raise TypeError(f"Expected VignetteParams, got {type(params)}")

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

            # ImageMagick vignette: -vignette {radius}x{sigma}+{x}+{y}
            # We use strength to control the effect
            # Higher strength = darker vignette
            vignette_arg = f"0x{params.strength}"
            cmd = [
                "convert",
                str(input_path),
                "-vignette",
                vignette_arg,
                str(output_path),
            ]

            # Run ImageMagick
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )

            if result.returncode != 0:
                raise ProcessingError(
                    f"ImageMagick vignette failed: {result.stderr}"
                )

            # Load result
            vignetted_image = Image.open(output_path)
            result_image = vignetted_image.copy()
            vignetted_image.close()

            return result_image

        finally:
            # Clean up temp files
            input_path.unlink(missing_ok=True)
            output_path.unlink(missing_ok=True)


class PILVignette(WallpaperEffect):
    """Vignette effect using PIL (fallback)."""

    @property
    def effect_name(self) -> str:
        """Get effect identifier."""
        return "vignette"

    @property
    def backend_name(self) -> str:
        """Get backend identifier."""
        return "pil"

    def is_available(self) -> bool:
        """PIL is always available."""
        return True

    def get_default_params(self) -> EffectParams:
        """Get default parameters."""
        return VignetteParams()

    def apply(self, image: Image.Image, params: EffectParams) -> Image.Image:
        """Apply vignette using PIL.

        Args:
            image: PIL Image object
            params: VignetteParams instance

        Returns:
            Vignetted PIL Image object
        """
        if not isinstance(params, VignetteParams):
            raise TypeError(f"Expected VignetteParams, got {type(params)}")

        # Create a radial gradient mask
        width, height = image.size
        mask = Image.new("L", (width, height), 0)
        _ = ImageDraw.Draw(mask)  # Unused but kept for potential future use

        # Calculate center and radius
        center_x, center_y = width // 2, height // 2
        max_radius = ((width / 2) ** 2 + (height / 2) ** 2) ** 0.5

        # Draw radial gradient
        # Strength controls how dark the vignette is
        strength_factor = params.strength / 100.0

        for y in range(height):
            for x in range(width):
                # Calculate distance from center
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                # Normalize distance
                normalized = distance / max_radius
                # Apply strength
                value = int(255 * (1 - normalized * strength_factor))
                value = max(0, min(255, value))
                mask.putpixel((x, y), value)

        # Apply mask to darken edges
        result = image.copy()
        result.putalpha(mask)
        # Composite with black background
        background = Image.new("RGB", image.size, (0, 0, 0))
        background.paste(result, mask=mask)

        return background

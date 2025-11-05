"""Effect backend implementations."""

from wallpaper_processor.backends.blur import ImageMagickBlur, PILBlur
from wallpaper_processor.backends.brightness import (
    ImageMagickBrightness,
    PILBrightness,
)
from wallpaper_processor.backends.color_overlay import (
    ImageMagickColorOverlay,
    PILColorOverlay,
)
from wallpaper_processor.backends.grayscale import (
    ImageMagickGrayscale,
    PILGrayscale,
)
from wallpaper_processor.backends.negate import ImageMagickNegate, PILNegate
from wallpaper_processor.backends.saturation import (
    ImageMagickSaturation,
    PILSaturation,
)
from wallpaper_processor.backends.vignette import (
    ImageMagickVignette,
    PILVignette,
)

__all__ = [
    # Blur
    "ImageMagickBlur",
    "PILBlur",
    # Brightness
    "ImageMagickBrightness",
    "PILBrightness",
    # Saturation
    "ImageMagickSaturation",
    "PILSaturation",
    # Vignette
    "ImageMagickVignette",
    "PILVignette",
    # Color Overlay
    "ImageMagickColorOverlay",
    "PILColorOverlay",
    # Grayscale
    "ImageMagickGrayscale",
    "PILGrayscale",
    # Negate
    "ImageMagickNegate",
    "PILNegate",
]

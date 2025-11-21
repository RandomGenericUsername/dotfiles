"""Effect backend implementations with auto-registration.

This module automatically discovers and imports all effect modules,
triggering their @register_effect decorators to populate the registry.
"""

import importlib
import pkgutil
from pathlib import Path

# Auto-discover and import all effect modules to trigger registration
package_dir = Path(__file__).parent
for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
    if not module_name.startswith("_"):
        importlib.import_module(f"wallpaper_processor.backends.{module_name}")

# Keep explicit imports for backwards compatibility
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

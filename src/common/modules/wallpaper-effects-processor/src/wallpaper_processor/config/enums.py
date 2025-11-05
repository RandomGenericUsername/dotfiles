"""Enumerations for wallpaper processor configuration."""

from enum import Enum


class ProcessingMode(str, Enum):
    """Processing mode for effect application."""

    MEMORY = "memory"  # Load image once, apply all effects in memory
    FILE = "file"  # Each effect reads/writes files (memory efficient)


class OutputFormat(str, Enum):
    """Supported output image formats."""

    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    WEBP = "webp"
    BMP = "bmp"
    TIFF = "tiff"


class EffectName(str, Enum):
    """Available effect names."""

    BLUR = "blur"
    BRIGHTNESS = "brightness"
    SATURATION = "saturation"
    VIGNETTE = "vignette"
    COLOR_OVERLAY = "color_overlay"


class BackendType(str, Enum):
    """Backend implementation types."""

    IMAGEMAGICK = "imagemagick"
    PIL = "pil"

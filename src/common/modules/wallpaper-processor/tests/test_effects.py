"""Tests for effect implementations."""

import pytest
from PIL import Image

from wallpaper_processor.backends import (
    ImageMagickBlur,
    ImageMagickBrightness,
    PILBlur,
    PILBrightness,
)
from wallpaper_processor.core.types import BlurParams, BrightnessParams


@pytest.fixture
def test_image():
    """Create a test image."""
    return Image.new("RGB", (100, 100), color=(128, 128, 128))


class TestPILBlur:
    """Tests for PIL blur effect."""

    def test_is_available(self):
        """Test that PIL blur is always available."""
        effect = PILBlur()
        assert effect.is_available()

    def test_effect_name(self):
        """Test effect name."""
        effect = PILBlur()
        assert effect.effect_name == "blur"

    def test_backend_name(self):
        """Test backend name."""
        effect = PILBlur()
        assert effect.backend_name == "pil"

    def test_apply(self, test_image):
        """Test applying blur effect."""
        effect = PILBlur()
        params = BlurParams(sigma=5)
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_get_default_params(self):
        """Test getting default parameters."""
        effect = PILBlur()
        params = effect.get_default_params()

        assert isinstance(params, BlurParams)
        assert params.sigma == 8
        assert params.radius == 0


class TestPILBrightness:
    """Tests for PIL brightness effect."""

    def test_is_available(self):
        """Test that PIL brightness is always available."""
        effect = PILBrightness()
        assert effect.is_available()

    def test_effect_name(self):
        """Test effect name."""
        effect = PILBrightness()
        assert effect.effect_name == "brightness"

    def test_backend_name(self):
        """Test backend name."""
        effect = PILBrightness()
        assert effect.backend_name == "pil"

    def test_apply_darken(self, test_image):
        """Test darkening image."""
        effect = PILBrightness()
        params = BrightnessParams(adjustment=-50)
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_apply_brighten(self, test_image):
        """Test brightening image."""
        effect = PILBrightness()
        params = BrightnessParams(adjustment=50)
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_get_default_params(self):
        """Test getting default parameters."""
        effect = PILBrightness()
        params = effect.get_default_params()

        assert isinstance(params, BrightnessParams)
        assert params.adjustment == -20


class TestImageMagickBlur:
    """Tests for ImageMagick blur effect."""

    def test_effect_name(self):
        """Test effect name."""
        effect = ImageMagickBlur()
        assert effect.effect_name == "blur"

    def test_backend_name(self):
        """Test backend name."""
        effect = ImageMagickBlur()
        assert effect.backend_name == "imagemagick"

    def test_get_default_params(self):
        """Test getting default parameters."""
        effect = ImageMagickBlur()
        params = effect.get_default_params()

        assert isinstance(params, BlurParams)


class TestImageMagickBrightness:
    """Tests for ImageMagick brightness effect."""

    def test_effect_name(self):
        """Test effect name."""
        effect = ImageMagickBrightness()
        assert effect.effect_name == "brightness"

    def test_backend_name(self):
        """Test backend name."""
        effect = ImageMagickBrightness()
        assert effect.backend_name == "imagemagick"

    def test_get_default_params(self):
        """Test getting default parameters."""
        effect = ImageMagickBrightness()
        params = effect.get_default_params()

        assert isinstance(params, BrightnessParams)


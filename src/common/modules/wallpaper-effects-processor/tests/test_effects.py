"""Tests for effect implementations."""

import pytest
from PIL import Image

from wallpaper_processor.backends import (
    ImageMagickBlur,
    ImageMagickBrightness,
    PILBlur,
    PILBrightness,
)
from wallpaper_processor.core.types import (
    BlurParams,
    BrightnessParams,
)


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


class TestPILSaturation:
    """Tests for PIL saturation effect."""

    def test_is_available(self):
        """Test that PIL saturation is always available."""
        from wallpaper_processor.backends import PILSaturation

        effect = PILSaturation()
        assert effect.is_available()

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import PILSaturation

        effect = PILSaturation()
        assert effect.effect_name == "saturation"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import PILSaturation

        effect = PILSaturation()
        assert effect.backend_name == "pil"

    def test_apply_increase(self, test_image):
        """Test increasing saturation."""
        from wallpaper_processor.backends import PILSaturation
        from wallpaper_processor.core.types import SaturationParams

        effect = PILSaturation()
        params = SaturationParams(adjustment=50)
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_apply_decrease(self, test_image):
        """Test decreasing saturation."""
        from wallpaper_processor.backends import PILSaturation
        from wallpaper_processor.core.types import SaturationParams

        effect = PILSaturation()
        params = SaturationParams(adjustment=-50)
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import PILSaturation
        from wallpaper_processor.core.types import SaturationParams

        effect = PILSaturation()
        params = effect.get_default_params()

        assert isinstance(params, SaturationParams)
        assert params.adjustment == 0


class TestPILVignette:
    """Tests for PIL vignette effect."""

    def test_is_available(self):
        """Test that PIL vignette is always available."""
        from wallpaper_processor.backends import PILVignette

        effect = PILVignette()
        assert effect.is_available()

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import PILVignette

        effect = PILVignette()
        assert effect.effect_name == "vignette"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import PILVignette

        effect = PILVignette()
        assert effect.backend_name == "pil"

    def test_apply(self, test_image):
        """Test applying vignette effect."""
        from wallpaper_processor.backends import PILVignette
        from wallpaper_processor.core.types import VignetteParams

        effect = PILVignette()
        params = VignetteParams(strength=30)
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import PILVignette
        from wallpaper_processor.core.types import VignetteParams

        effect = PILVignette()
        params = effect.get_default_params()

        assert isinstance(params, VignetteParams)
        assert params.strength == 20


class TestPILColorOverlay:
    """Tests for PIL color overlay effect."""

    def test_is_available(self):
        """Test that PIL color overlay is always available."""
        from wallpaper_processor.backends import PILColorOverlay

        effect = PILColorOverlay()
        assert effect.is_available()

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import PILColorOverlay

        effect = PILColorOverlay()
        assert effect.effect_name == "color_overlay"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import PILColorOverlay

        effect = PILColorOverlay()
        assert effect.backend_name == "pil"

    def test_apply(self, test_image):
        """Test applying color overlay effect."""
        from wallpaper_processor.backends import PILColorOverlay
        from wallpaper_processor.core.types import ColorOverlayParams

        effect = PILColorOverlay()
        params = ColorOverlayParams(color="#ff00ff", opacity=0.3)
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import PILColorOverlay
        from wallpaper_processor.core.types import ColorOverlayParams

        effect = PILColorOverlay()
        params = effect.get_default_params()

        assert isinstance(params, ColorOverlayParams)
        assert params.color == "#000000"
        assert params.opacity == 0.3


class TestPILGrayscale:
    """Tests for PIL grayscale effect."""

    def test_is_available(self):
        """Test that PIL grayscale is always available."""
        from wallpaper_processor.backends import PILGrayscale

        effect = PILGrayscale()
        assert effect.is_available()

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import PILGrayscale

        effect = PILGrayscale()
        assert effect.effect_name == "grayscale"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import PILGrayscale

        effect = PILGrayscale()
        assert effect.backend_name == "pil"

    def test_apply(self, test_image):
        """Test applying grayscale effect."""
        from wallpaper_processor.backends import PILGrayscale
        from wallpaper_processor.core.types import GrayscaleParams

        effect = PILGrayscale()
        params = GrayscaleParams()
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import PILGrayscale
        from wallpaper_processor.core.types import GrayscaleParams

        effect = PILGrayscale()
        params = effect.get_default_params()

        assert isinstance(params, GrayscaleParams)
        assert params.method == "average"


class TestPILNegate:
    """Tests for PIL negate effect."""

    def test_is_available(self):
        """Test that PIL negate is always available."""
        from wallpaper_processor.backends import PILNegate

        effect = PILNegate()
        assert effect.is_available()

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import PILNegate

        effect = PILNegate()
        assert effect.effect_name == "negate"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import PILNegate

        effect = PILNegate()
        assert effect.backend_name == "pil"

    def test_apply(self, test_image):
        """Test applying negate effect."""
        from wallpaper_processor.backends import PILNegate
        from wallpaper_processor.core.types import NegateParams

        effect = PILNegate()
        params = NegateParams()
        result = effect.apply(test_image, params)

        assert isinstance(result, Image.Image)
        assert result.size == test_image.size

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import PILNegate
        from wallpaper_processor.core.types import NegateParams

        effect = PILNegate()
        params = effect.get_default_params()

        assert isinstance(params, NegateParams)


class TestImageMagickSaturation:
    """Tests for ImageMagick saturation effect."""

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import ImageMagickSaturation

        effect = ImageMagickSaturation()
        assert effect.effect_name == "saturation"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import ImageMagickSaturation

        effect = ImageMagickSaturation()
        assert effect.backend_name == "imagemagick"

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import ImageMagickSaturation
        from wallpaper_processor.core.types import SaturationParams

        effect = ImageMagickSaturation()
        params = effect.get_default_params()

        assert isinstance(params, SaturationParams)


class TestImageMagickVignette:
    """Tests for ImageMagick vignette effect."""

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import ImageMagickVignette

        effect = ImageMagickVignette()
        assert effect.effect_name == "vignette"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import ImageMagickVignette

        effect = ImageMagickVignette()
        assert effect.backend_name == "imagemagick"

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import ImageMagickVignette
        from wallpaper_processor.core.types import VignetteParams

        effect = ImageMagickVignette()
        params = effect.get_default_params()

        assert isinstance(params, VignetteParams)


class TestImageMagickColorOverlay:
    """Tests for ImageMagick color overlay effect."""

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import ImageMagickColorOverlay

        effect = ImageMagickColorOverlay()
        assert effect.effect_name == "color_overlay"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import ImageMagickColorOverlay

        effect = ImageMagickColorOverlay()
        assert effect.backend_name == "imagemagick"

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import ImageMagickColorOverlay
        from wallpaper_processor.core.types import ColorOverlayParams

        effect = ImageMagickColorOverlay()
        params = effect.get_default_params()

        assert isinstance(params, ColorOverlayParams)


class TestImageMagickGrayscale:
    """Tests for ImageMagick grayscale effect."""

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import ImageMagickGrayscale

        effect = ImageMagickGrayscale()
        assert effect.effect_name == "grayscale"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import ImageMagickGrayscale

        effect = ImageMagickGrayscale()
        assert effect.backend_name == "imagemagick"

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import ImageMagickGrayscale
        from wallpaper_processor.core.types import GrayscaleParams

        effect = ImageMagickGrayscale()
        params = effect.get_default_params()

        assert isinstance(params, GrayscaleParams)


class TestImageMagickNegate:
    """Tests for ImageMagick negate effect."""

    def test_effect_name(self):
        """Test effect name."""
        from wallpaper_processor.backends import ImageMagickNegate

        effect = ImageMagickNegate()
        assert effect.effect_name == "negate"

    def test_backend_name(self):
        """Test backend name."""
        from wallpaper_processor.backends import ImageMagickNegate

        effect = ImageMagickNegate()
        assert effect.backend_name == "imagemagick"

    def test_get_default_params(self):
        """Test getting default parameters."""
        from wallpaper_processor.backends import ImageMagickNegate
        from wallpaper_processor.core.types import NegateParams

        effect = ImageMagickNegate()
        params = effect.get_default_params()

        assert isinstance(params, NegateParams)

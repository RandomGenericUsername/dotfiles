"""Tests for base WallpaperEffect class."""

import pytest
from PIL import Image

from wallpaper_processor.backends import PILBlur
from wallpaper_processor.core.exceptions import EffectNotAvailableError
from wallpaper_processor.core.types import BlurParams


class TestWallpaperEffectBase:
    """Tests for WallpaperEffect base class methods."""

    def test_apply_to_file(self, tmp_path):
        """Test apply_to_file method."""
        # Create test image
        input_path = tmp_path / "input.png"
        output_path = tmp_path / "output.png"

        image = Image.new("RGB", (100, 100), color=(128, 128, 128))
        image.save(input_path)

        # Apply effect
        effect = PILBlur()
        params = BlurParams(sigma=5)
        result = effect.apply_to_file(input_path, output_path, params)

        assert result == output_path
        assert output_path.exists()

    def test_apply_to_file_not_found(self, tmp_path):
        """Test apply_to_file with nonexistent input file."""
        input_path = tmp_path / "nonexistent.png"
        output_path = tmp_path / "output.png"

        effect = PILBlur()
        params = BlurParams(sigma=5)

        with pytest.raises(FileNotFoundError):
            effect.apply_to_file(input_path, output_path, params)

    def test_ensure_available_success(self):
        """Test ensure_available with available effect."""
        effect = PILBlur()
        # Should not raise
        effect.ensure_available()

    def test_ensure_available_failure(self):
        """Test ensure_available with unavailable effect."""

        from wallpaper_processor.core.base import WallpaperEffect
        from wallpaper_processor.core.types import EffectParams

        # Create a mock effect that is not available
        class UnavailableEffect(WallpaperEffect):
            def apply(
                self, image: Image.Image, params: EffectParams
            ) -> Image.Image:
                return image

            def is_available(self) -> bool:
                return False

            @property
            def effect_name(self) -> str:
                return "test_effect"

            @property
            def backend_name(self) -> str:
                return "test_backend"

            def get_default_params(self) -> EffectParams:
                return BlurParams()

        effect = UnavailableEffect()

        with pytest.raises(EffectNotAvailableError) as exc_info:
            effect.ensure_available()

        assert "test_effect" in str(exc_info.value)
        assert "test_backend" in str(exc_info.value)

    def test_effect_properties(self):
        """Test effect properties."""
        effect = PILBlur()

        assert effect.effect_name == "blur"
        assert effect.backend_name == "pil"
        assert effect.is_available() is True

    def test_get_default_params(self):
        """Test get_default_params method."""
        effect = PILBlur()
        params = effect.get_default_params()

        assert isinstance(params, BlurParams)
        assert params.sigma == 8
        assert params.radius == 0

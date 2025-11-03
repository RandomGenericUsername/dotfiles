"""Tests for effect factory."""

import pytest
from wallpaper_processor.config import AppConfig
from wallpaper_processor.core.exceptions import PresetNotFoundError
from wallpaper_processor.factory import EffectFactory
from wallpaper_processor.pipeline import EffectPipeline


class TestEffectFactory:
    """Tests for EffectFactory."""

    def test_create_blur(self):
        """Test creating blur effect."""
        config = AppConfig()
        effect = EffectFactory.create("blur", config)

        assert effect is not None
        assert effect.effect_name == "blur"

    def test_create_brightness(self):
        """Test creating brightness effect."""
        config = AppConfig()
        effect = EffectFactory.create("brightness", config)

        assert effect is not None
        assert effect.effect_name == "brightness"

    def test_create_unknown_effect(self):
        """Test creating unknown effect raises error."""
        config = AppConfig()

        with pytest.raises(ValueError, match="Unknown effect"):
            EffectFactory.create("unknown", config)

    def test_create_from_preset(self):
        """Test creating pipeline from preset."""
        config = AppConfig()
        # Assuming dark_blur preset exists in default config
        pipeline = EffectFactory.create_from_preset("dark_blur", config)

        assert isinstance(pipeline, EffectPipeline)
        assert len(pipeline.effects) > 0

    def test_create_from_nonexistent_preset(self):
        """Test creating from nonexistent preset raises error."""
        config = AppConfig()

        with pytest.raises(PresetNotFoundError):
            EffectFactory.create_from_preset("nonexistent", config)

    def test_list_available_effects(self):
        """Test listing available effects."""
        config = AppConfig()
        available = EffectFactory.list_available_effects(config)

        assert isinstance(available, dict)
        assert "blur" in available
        assert "brightness" in available
        assert "pil" in available["blur"]

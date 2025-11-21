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
        from wallpaper_processor.config import get_default_config

        config = (
            get_default_config()
        )  # Load config with presets from settings.toml
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

    def test_create_saturation(self):
        """Test creating saturation effect."""
        config = AppConfig()
        effect = EffectFactory.create("saturation", config)

        assert effect is not None
        assert effect.effect_name == "saturation"

    def test_create_vignette(self):
        """Test creating vignette effect."""
        config = AppConfig()
        effect = EffectFactory.create("vignette", config)

        assert effect is not None
        assert effect.effect_name == "vignette"

    def test_create_color_overlay(self):
        """Test creating color_overlay effect."""
        config = AppConfig()
        effect = EffectFactory.create("color_overlay", config)

        assert effect is not None
        assert effect.effect_name == "color_overlay"

    def test_create_grayscale(self):
        """Test creating grayscale effect."""
        config = AppConfig()
        effect = EffectFactory.create("grayscale", config)

        assert effect is not None
        assert effect.effect_name == "grayscale"

    def test_create_negate(self):
        """Test creating negate effect."""
        config = AppConfig()
        effect = EffectFactory.create("negate", config)

        assert effect is not None
        assert effect.effect_name == "negate"

    def test_create_with_pil_preference(self):
        """Test creating effect with PIL preference."""
        from wallpaper_processor.config.config import BackendConfig

        config = AppConfig(backend=BackendConfig(prefer_imagemagick=False))
        effect = EffectFactory.create("blur", config)

        assert effect is not None
        assert effect.backend_name == "pil"

    def test_get_all_effect_names(self):
        """Test getting all effect names from dynamic registry."""
        names = EffectFactory.get_all_effect_names()

        assert isinstance(names, list)
        # Should have at least the 7 core effects (dynamic registry may have more)
        assert len(names) >= 7
        # Verify all core effects are present
        assert "blur" in names
        assert "brightness" in names
        assert "saturation" in names
        assert "vignette" in names
        assert "color_overlay" in names
        assert "grayscale" in names
        assert "negate" in names

    def test_list_available_effects_all_effects(self):
        """Test that all effects are listed as available."""
        config = AppConfig()
        available = EffectFactory.list_available_effects(config)

        # All effects should be available via PIL at minimum
        assert "blur" in available
        assert "brightness" in available
        assert "saturation" in available
        assert "vignette" in available
        assert "color_overlay" in available
        assert "grayscale" in available
        assert "negate" in available

    def test_create_from_preset_with_config(self):
        """Test creating pipeline from preset with custom config."""
        from wallpaper_processor.config import get_default_config
        from wallpaper_processor.core.types import (
            ProcessingMode,
            ProcessorConfig,
        )

        config = get_default_config()
        processor_config = ProcessorConfig(processing_mode=ProcessingMode.FILE)
        pipeline = EffectFactory.create_from_preset(
            "dark_blur", config, processor_config
        )

        assert isinstance(pipeline, EffectPipeline)
        assert pipeline.config.processing_mode == ProcessingMode.FILE

    def test_create_from_preset_multiple_presets(self):
        """Test creating pipelines from different presets."""
        from wallpaper_processor.config import get_default_config

        config = get_default_config()

        dark_blur = EffectFactory.create_from_preset("dark_blur", config)
        aesthetic = EffectFactory.create_from_preset("aesthetic", config)
        lockscreen = EffectFactory.create_from_preset("lockscreen", config)

        assert len(dark_blur.effects) == 2
        assert len(aesthetic.effects) == 3
        assert len(lockscreen.effects) == 3

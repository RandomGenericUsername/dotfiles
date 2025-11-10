"""Tests for PresetManager."""

import pytest

from wallpaper_processor.config import AppConfig, Preset, PresetEffect, get_default_config
from wallpaper_processor.core.exceptions import PresetNotFoundError
from wallpaper_processor.core.managers.preset import PresetManager


class TestPresetManager:
    """Tests for PresetManager."""

    def test_init(self, mock_app_config):
        """Test PresetManager initialization."""
        manager = PresetManager(mock_app_config)
        assert manager.settings == mock_app_config

    def test_get_preset_success(self, mock_app_config_with_presets):
        """Test getting an existing preset."""
        manager = PresetManager(mock_app_config_with_presets)
        preset = manager.get_preset("test_preset")

        assert isinstance(preset, Preset)
        assert preset.description == "Test preset"
        assert len(preset.effects) == 2
        assert preset.effects[0].name == "blur"
        assert preset.effects[1].name == "brightness"

    def test_get_preset_not_found(self, mock_app_config):
        """Test getting a non-existent preset raises error."""
        manager = PresetManager(mock_app_config)

        with pytest.raises(PresetNotFoundError) as exc_info:
            manager.get_preset("nonexistent")

        assert exc_info.value.preset_name == "nonexistent"

    def test_list_presets_empty(self, mock_app_config):
        """Test listing presets when none exist."""
        manager = PresetManager(mock_app_config)
        presets = manager.list_presets()

        assert isinstance(presets, dict)
        assert len(presets) == 0

    def test_list_presets_with_presets(self, mock_app_config_with_presets):
        """Test listing presets when they exist."""
        manager = PresetManager(mock_app_config_with_presets)
        presets = manager.list_presets()

        assert isinstance(presets, dict)
        assert len(presets) == 1
        assert "test_preset" in presets
        assert presets["test_preset"] == "Test preset"

    def test_list_presets_from_default_config(self):
        """Test listing presets from default config."""
        config = get_default_config()
        manager = PresetManager(config)
        presets = manager.list_presets()

        assert isinstance(presets, dict)
        assert len(presets) > 0
        assert "dark_blur" in presets
        assert "aesthetic" in presets
        assert "lockscreen" in presets
        assert "minimal_dark" in presets

    def test_preset_exists_true(self, mock_app_config_with_presets):
        """Test preset_exists returns True for existing preset."""
        manager = PresetManager(mock_app_config_with_presets)
        assert manager.preset_exists("test_preset") is True

    def test_preset_exists_false(self, mock_app_config):
        """Test preset_exists returns False for non-existent preset."""
        manager = PresetManager(mock_app_config)
        assert manager.preset_exists("nonexistent") is False

    def test_get_preset_with_default_config(self):
        """Test getting preset from default config."""
        config = get_default_config()
        manager = PresetManager(config)
        preset = manager.get_preset("dark_blur")

        assert isinstance(preset, Preset)
        assert preset.description == "Blurred and darkened for better text readability"
        assert len(preset.effects) == 2
        assert preset.effects[0].name == "blur"
        assert preset.effects[0].params["sigma"] == 6
        assert preset.effects[1].name == "brightness"
        assert preset.effects[1].params["adjustment"] == -15

    def test_get_multiple_presets(self):
        """Test getting multiple different presets."""
        config = get_default_config()
        manager = PresetManager(config)

        dark_blur = manager.get_preset("dark_blur")
        aesthetic = manager.get_preset("aesthetic")
        lockscreen = manager.get_preset("lockscreen")

        assert dark_blur.description == "Blurred and darkened for better text readability"
        assert aesthetic.description == "Aesthetic vaporwave style"
        assert lockscreen.description == "Heavy blur for lockscreen backgrounds"

    def test_preset_effects_structure(self):
        """Test that preset effects have correct structure."""
        config = get_default_config()
        manager = PresetManager(config)
        preset = manager.get_preset("aesthetic")

        assert len(preset.effects) == 3
        for effect in preset.effects:
            assert isinstance(effect, PresetEffect)
            assert hasattr(effect, "name")
            assert hasattr(effect, "params")
            assert isinstance(effect.name, str)
            assert isinstance(effect.params, dict)

    def test_preset_params_types(self):
        """Test that preset params have correct types."""
        config = get_default_config()
        manager = PresetManager(config)
        preset = manager.get_preset("dark_blur")

        blur_effect = preset.effects[0]
        assert blur_effect.name == "blur"
        assert isinstance(blur_effect.params["sigma"], (int, float))

        brightness_effect = preset.effects[1]
        assert brightness_effect.name == "brightness"
        assert isinstance(brightness_effect.params["adjustment"], int)

    def test_multiple_managers_with_same_config(self, mock_app_config_with_presets):
        """Test creating multiple managers with same config."""
        manager1 = PresetManager(mock_app_config_with_presets)
        manager2 = PresetManager(mock_app_config_with_presets)

        preset1 = manager1.get_preset("test_preset")
        preset2 = manager2.get_preset("test_preset")

        assert preset1.description == preset2.description
        assert len(preset1.effects) == len(preset2.effects)

    def test_manager_with_complex_preset(self):
        """Test manager with a complex preset (multiple effects)."""
        config = get_default_config()
        manager = PresetManager(config)
        preset = manager.get_preset("lockscreen")

        # lockscreen has 3 effects: blur, brightness, saturation
        assert len(preset.effects) == 3
        assert preset.effects[0].name == "blur"
        assert preset.effects[1].name == "brightness"
        assert preset.effects[2].name == "saturation"

    def test_list_presets_returns_all_descriptions(self):
        """Test that list_presets returns all preset descriptions."""
        config = get_default_config()
        manager = PresetManager(config)
        presets = manager.list_presets()

        # Verify all presets have descriptions
        for name, description in presets.items():
            assert isinstance(name, str)
            assert isinstance(description, str)
            assert len(description) > 0

    def test_preset_exists_with_default_config(self):
        """Test preset_exists with default config presets."""
        config = get_default_config()
        manager = PresetManager(config)

        assert manager.preset_exists("dark_blur") is True
        assert manager.preset_exists("aesthetic") is True
        assert manager.preset_exists("lockscreen") is True
        assert manager.preset_exists("minimal_dark") is True
        assert manager.preset_exists("nonexistent") is False

    def test_get_preset_immutability(self, mock_app_config_with_presets):
        """Test that getting preset doesn't modify the original."""
        manager = PresetManager(mock_app_config_with_presets)
        preset1 = manager.get_preset("test_preset")
        preset2 = manager.get_preset("test_preset")

        # Both should have same values
        assert preset1.description == preset2.description
        assert len(preset1.effects) == len(preset2.effects)


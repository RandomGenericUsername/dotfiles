"""Tests for configuration."""

import pytest
from wallpaper_orchestrator.config import (
    AppConfig,
    ContainerConfig,
    ProcessingConfig,
    get_default_config,
)


class TestContainerConfig:
    """Tests for ContainerConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ContainerConfig()

        assert config.runtime == "docker"
        assert config.image_name == "wallpaper-processor"
        assert config.image_tag == "latest"
        assert config.build_no_cache is False
        assert config.build_pull is True

    def test_custom_values(self):
        """Test custom configuration values."""
        config = ContainerConfig(
            runtime="podman",
            image_name="custom-processor",
            image_tag="v1.0",
        )

        assert config.runtime == "podman"
        assert config.image_name == "custom-processor"
        assert config.image_tag == "v1.0"


class TestProcessingConfig:
    """Tests for ProcessingConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ProcessingConfig()

        assert config.mode == "memory"
        assert config.output_format == "png"
        assert config.quality == 95
        assert config.write_metadata is False

    def test_quality_validation(self):
        """Test quality validation."""
        # Valid quality
        config = ProcessingConfig(quality=50)
        assert config.quality == 50

        # Invalid quality (too low)
        with pytest.raises(ValueError):
            ProcessingConfig(quality=0)

        # Invalid quality (too high)
        with pytest.raises(ValueError):
            ProcessingConfig(quality=101)


class TestAppConfig:
    """Tests for AppConfig."""

    def test_default_config(self):
        """Test default application configuration."""
        config = AppConfig()

        assert isinstance(config.container, ContainerConfig)
        assert isinstance(config.processing, ProcessingConfig)
        assert isinstance(config.presets, dict)

    def test_load_default_config(self):
        """Test loading default configuration."""
        config = get_default_config()

        assert isinstance(config, AppConfig)
        assert config.container.runtime in ("docker", "podman")
        assert len(config.presets) > 0

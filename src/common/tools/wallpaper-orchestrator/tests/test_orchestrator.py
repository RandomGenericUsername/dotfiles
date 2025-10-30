"""Tests for orchestrator."""

import pytest

from wallpaper_orchestrator.config import AppConfig
from wallpaper_orchestrator.orchestrator import WallpaperOrchestrator


class TestWallpaperOrchestrator:
    """Tests for WallpaperOrchestrator."""

    def test_initialization(self):
        """Test orchestrator initialization."""
        config = AppConfig()
        orchestrator = WallpaperOrchestrator(config)

        assert orchestrator.config == config
        assert orchestrator.registry is not None
        assert orchestrator.builder is not None
        assert orchestrator.runner is not None

    def test_config_propagation(self):
        """Test configuration propagates to components."""
        config = AppConfig()
        config.container.runtime = "podman"

        orchestrator = WallpaperOrchestrator(config)

        assert orchestrator.registry.config.runtime == "podman"


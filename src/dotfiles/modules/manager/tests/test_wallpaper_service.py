"""Tests for WallpaperService."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from wallpaper_orchestrator import WallpaperResult

from dotfiles_manager.models.system_attributes import SystemAttributes
from dotfiles_manager.services.wallpaper_service import WallpaperService


@pytest.fixture
def mock_orchestrator():
    """Create mock wallpaper orchestrator."""
    orchestrator = Mock()
    return orchestrator


@pytest.fixture
def mock_wallpaper_state_repo():
    """Create mock wallpaper state repository."""
    repo = Mock()
    repo.is_wallpaper_cached.return_value = False
    return repo


@pytest.fixture
def mock_system_attributes_repo():
    """Create mock system attributes repository."""
    repo = Mock()
    repo.get_attributes.return_value = SystemAttributes(
        font_family="JetBrains Mono",
        font_size=12,
    )
    return repo


@pytest.fixture
def mock_hook_registry():
    """Create mock hook registry."""
    registry = Mock()
    registry.execute_all.return_value = {}
    return registry


@pytest.fixture
def wallpaper_service(
    mock_orchestrator,
    mock_wallpaper_state_repo,
    mock_system_attributes_repo,
    mock_hook_registry,
):
    """Create WallpaperService instance."""
    return WallpaperService(
        orchestrator=mock_orchestrator,
        wallpaper_state_repo=mock_wallpaper_state_repo,
        system_attributes_repo=mock_system_attributes_repo,
        hook_registry=mock_hook_registry,
    )


@pytest.fixture
def wallpaper_path(tmp_path):
    """Create temporary wallpaper file."""
    wallpaper = tmp_path / "wallpaper.png"
    wallpaper.touch()
    return wallpaper


@pytest.fixture
def colorscheme_files(tmp_path):
    """Create temporary colorscheme files."""
    colorscheme_dir = tmp_path / "colorscheme"
    colorscheme_dir.mkdir()

    json_path = colorscheme_dir / "colors.json"
    json_path.touch()

    return {"json": json_path}


def test_change_wallpaper_passes_generation_flags_to_hook_context(
    wallpaper_service,
    mock_orchestrator,
    mock_hook_registry,
    wallpaper_path,
    colorscheme_files,
    tmp_path,
):
    """Test that change_wallpaper passes colorscheme_generated and effects_generated to HookContext."""
    # Arrange
    effects_dir = tmp_path / "effects"
    effects_dir.mkdir()

    mock_orchestrator.process.return_value = WallpaperResult(
        original_wallpaper=wallpaper_path,
        effects_output_dir=effects_dir,
        colorscheme_output_dir=tmp_path / "colorscheme",
        colorscheme_files=colorscheme_files,
        effect_variants={},
        colorscheme_generated=True,  # Colorscheme was generated
        effects_generated=False,  # Effects were not generated
        wallpaper_set=True,
        monitor_set="eDP-2",
    )

    # Act
    wallpaper_service.change_wallpaper(
        wallpaper_path=wallpaper_path,
        monitor="eDP-2",
        generate_colorscheme=True,
        generate_effects=False,
    )

    # Assert
    # Verify hook registry was called with correct context
    mock_hook_registry.execute_all.assert_called_once()
    hook_context = mock_hook_registry.execute_all.call_args[0][0]

    assert hook_context.wallpaper_path == wallpaper_path
    assert hook_context.colorscheme_files == colorscheme_files
    assert hook_context.colorscheme_generated is True
    assert hook_context.effects_generated is False
    assert hook_context.font_family == "JetBrains Mono"
    assert hook_context.font_size == 12
    assert hook_context.monitor == "eDP-2"


def test_change_wallpaper_with_no_colorscheme_flag(
    wallpaper_service,
    mock_orchestrator,
    mock_hook_registry,
    wallpaper_path,
    tmp_path,
):
    """Test change_wallpaper with --no-colorscheme flag."""
    # Arrange
    effects_dir = tmp_path / "effects"
    effects_dir.mkdir()

    mock_orchestrator.process.return_value = WallpaperResult(
        original_wallpaper=wallpaper_path,
        effects_output_dir=effects_dir,
        colorscheme_output_dir=tmp_path / "colorscheme",
        colorscheme_files={},  # Empty - no colorscheme generated
        effect_variants={"blur": Path("/path/to/blur.png")},
        colorscheme_generated=False,  # Not generated
        effects_generated=True,  # Generated
        wallpaper_set=True,
        monitor_set="eDP-2",
    )

    # Act
    wallpaper_service.change_wallpaper(
        wallpaper_path=wallpaper_path,
        monitor="eDP-2",
        generate_colorscheme=False,
        generate_effects=True,
    )

    # Assert
    hook_context = mock_hook_registry.execute_all.call_args[0][0]
    assert hook_context.colorscheme_generated is False
    assert hook_context.effects_generated is True
    assert hook_context.colorscheme_files == {}

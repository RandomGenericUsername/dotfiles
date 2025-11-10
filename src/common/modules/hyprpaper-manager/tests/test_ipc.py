"""Tests for IPC client."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from hyprpaper_manager.core.exceptions import (
    HyprpaperNotRunningError,
)
from hyprpaper_manager.ipc.client import HyprpaperIPC


@pytest.fixture
def ipc():
    """Create IPC client."""
    return HyprpaperIPC(timeout=5)


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_is_running_true(mock_run, ipc):
    """Test is_running returns True."""
    mock_run.return_value = Mock(returncode=0)
    assert ipc.is_running() is True


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_is_running_false(mock_run, ipc):
    """Test is_running returns False."""
    mock_run.return_value = Mock(returncode=1)
    assert ipc.is_running() is False


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_preload_success(mock_run, ipc):
    """Test preload command."""
    # is_ready() calls subprocess.run multiple times, then the actual command
    mock_run.return_value = Mock(returncode=0, stdout="ok")

    ipc.preload(Path("/test/wallpaper.png"))

    # Check that hyprctl was called
    assert mock_run.call_count >= 1
    # Find the preload call
    preload_calls = [
        call
        for call in mock_run.call_args_list
        if len(call[0]) > 0 and "preload" in str(call[0][0])
    ]
    assert len(preload_calls) >= 1
    call_args = preload_calls[0][0][0]
    assert "hyprctl" in call_args
    assert "hyprpaper" in call_args
    assert "preload" in call_args


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_preload_not_running(mock_run, ipc):
    """Test preload when hyprpaper not running."""
    mock_run.return_value = Mock(returncode=1)  # is_running returns False

    with pytest.raises(HyprpaperNotRunningError):
        ipc.preload(Path("/test/wallpaper.png"))


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_wallpaper_success(mock_run, ipc):
    """Test wallpaper command."""
    mock_run.return_value = Mock(returncode=0, stdout="ok")

    ipc.wallpaper("DP-1", Path("/test/wallpaper.png"))

    assert mock_run.call_count >= 1
    # Find the wallpaper call
    wallpaper_calls = [
        call
        for call in mock_run.call_args_list
        if len(call[0]) > 0 and "wallpaper" in str(call[0][0])
    ]
    assert len(wallpaper_calls) >= 1


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_listloaded_success(mock_run, ipc):
    """Test listloaded command."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="/path/to/wallpaper1.png\n/path/to/wallpaper2.png",
    )

    wallpapers = ipc.listloaded()

    assert len(wallpapers) == 2
    assert all(isinstance(wp, Path) for wp in wallpapers)


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_listactive_success(mock_run, ipc):
    """Test listactive command."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="DP-1 = /path/to/wallpaper.png",
    )

    active = ipc.listactive()

    assert len(active) == 1
    assert "DP-1" in active
    assert isinstance(active["DP-1"], Path)

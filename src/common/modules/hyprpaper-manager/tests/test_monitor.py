"""Tests for monitor management."""

import json
from unittest.mock import Mock, patch

import pytest

from hyprpaper_manager.core.exceptions import MonitorNotFoundError
from hyprpaper_manager.core.types import MonitorInfo
from hyprpaper_manager.monitor import MonitorManager


@pytest.fixture
def monitor_manager():
    """Create monitor manager."""
    return MonitorManager(timeout=5)


@pytest.fixture
def mock_monitors_data():
    """Create mock monitors data."""
    return [
        {
            "name": "DP-1",
            "description": "Dell Monitor",
            "focused": True,
        },
        {
            "name": "HDMI-1",
            "description": "Samsung Monitor",
            "focused": False,
        },
    ]


class TestMonitorManager:
    def test_monitor_manager_initialization(self, monitor_manager):
        """Test MonitorManager initialization."""
        assert monitor_manager.timeout == 5

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_monitors_success(
        self, mock_run, monitor_manager, mock_monitors_data
    ):
        """Test getting monitors successfully."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(mock_monitors_data),
        )

        monitors = monitor_manager.get_monitors()

        assert len(monitors) == 2
        assert all(isinstance(m, MonitorInfo) for m in monitors)
        assert monitors[0].name == "DP-1"
        assert monitors[0].description == "Dell Monitor"
        assert monitors[0].focused is True
        assert monitors[1].name == "HDMI-1"
        assert monitors[1].description == "Samsung Monitor"
        assert monitors[1].focused is False

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_monitors_empty(self, mock_run, monitor_manager):
        """Test getting monitors when none exist."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="[]",
        )

        monitors = monitor_manager.get_monitors()

        assert monitors == []

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_monitors_subprocess_error(self, mock_run, monitor_manager):
        """Test getting monitors when subprocess fails."""
        mock_run.side_effect = FileNotFoundError()

        monitors = monitor_manager.get_monitors()

        # Should return empty list on error
        assert monitors == []

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_monitors_json_decode_error(self, mock_run, monitor_manager):
        """Test getting monitors with invalid JSON."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="invalid json",
        )

        monitors = monitor_manager.get_monitors()

        # Should return empty list on JSON error
        assert monitors == []

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_focused_monitor_success(
        self, mock_run, monitor_manager, mock_monitors_data
    ):
        """Test getting focused monitor."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(mock_monitors_data),
        )

        focused = monitor_manager.get_focused_monitor()

        assert focused.name == "DP-1"
        assert focused.focused is True

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_focused_monitor_not_found(self, mock_run, monitor_manager):
        """Test getting focused monitor when none focused."""
        monitors_data = [
            {"name": "DP-1", "focused": False},
            {"name": "HDMI-1", "focused": False},
        ]
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(monitors_data),
        )

        with pytest.raises(MonitorNotFoundError) as exc_info:
            monitor_manager.get_focused_monitor()

        assert "No focused monitor" in str(exc_info.value)

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_monitor_success(
        self, mock_run, monitor_manager, mock_monitors_data
    ):
        """Test getting specific monitor by name."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(mock_monitors_data),
        )

        monitor = monitor_manager.get_monitor("HDMI-1")

        assert monitor.name == "HDMI-1"
        assert monitor.description == "Samsung Monitor"
        assert monitor.focused is False

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_monitor_not_found(
        self, mock_run, monitor_manager, mock_monitors_data
    ):
        """Test getting monitor that doesn't exist."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(mock_monitors_data),
        )

        with pytest.raises(MonitorNotFoundError) as exc_info:
            monitor_manager.get_monitor("DVI-1")

        assert "DVI-1" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_monitors_with_missing_fields(self, mock_run, monitor_manager):
        """Test getting monitors with missing optional fields."""
        monitors_data = [
            {"name": "DP-1"},  # Missing description and focused
        ]
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(monitors_data),
        )

        monitors = monitor_manager.get_monitors()

        assert len(monitors) == 1
        assert monitors[0].name == "DP-1"
        assert monitors[0].description is None
        assert monitors[0].focused is False

    @patch("hyprpaper_manager.monitor.subprocess.run")
    def test_get_monitors_timeout(self, mock_run, monitor_manager):
        """Test getting monitors with custom timeout."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="[]",
        )

        monitor_manager.get_monitors()

        # Verify timeout was passed to subprocess.run
        call_args = mock_run.call_args
        assert call_args[1]["timeout"] == 5

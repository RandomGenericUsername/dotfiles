"""Tests for custom exceptions."""

import pytest

from hyprpaper_manager.core.exceptions import (
    HyprpaperError,
    HyprpaperIPCError,
    HyprpaperNotRunningError,
    MonitorNotFoundError,
    WallpaperNotFoundError,
    WallpaperNotLoadedError,
    WallpaperTooLargeError,
)


class TestHyprpaperError:
    def test_hyprpaper_error_creation(self):
        """Test HyprpaperError creation."""
        error = HyprpaperError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_hyprpaper_error_raise(self):
        """Test raising HyprpaperError."""
        with pytest.raises(HyprpaperError) as exc_info:
            raise HyprpaperError("Test error")
        assert "Test error" in str(exc_info.value)


class TestHyprpaperNotRunningError:
    def test_not_running_error_creation(self):
        """Test HyprpaperNotRunningError creation."""
        error = HyprpaperNotRunningError("hyprpaper is not running")
        assert str(error) == "hyprpaper is not running"
        assert isinstance(error, HyprpaperError)

    def test_not_running_error_raise(self):
        """Test raising HyprpaperNotRunningError."""
        with pytest.raises(HyprpaperNotRunningError) as exc_info:
            raise HyprpaperNotRunningError("hyprpaper is not running")
        assert "not running" in str(exc_info.value)


class TestHyprpaperIPCError:
    def test_ipc_error_basic(self):
        """Test HyprpaperIPCError with basic message."""
        error = HyprpaperIPCError("IPC failed")
        assert str(error) == "IPC failed"
        assert error.command is None
        assert error.exit_code is None
        assert isinstance(error, HyprpaperError)

    def test_ipc_error_with_command(self):
        """Test HyprpaperIPCError with command."""
        error = HyprpaperIPCError("IPC failed", command="preload")
        assert str(error) == "IPC failed"
        assert error.command == "preload"
        assert error.exit_code is None

    def test_ipc_error_with_exit_code(self):
        """Test HyprpaperIPCError with exit code."""
        error = HyprpaperIPCError("IPC failed", exit_code=1)
        assert str(error) == "IPC failed"
        assert error.command is None
        assert error.exit_code == 1

    def test_ipc_error_with_all_params(self):
        """Test HyprpaperIPCError with all parameters."""
        error = HyprpaperIPCError(
            "IPC failed",
            command="wallpaper",
            exit_code=2,
        )
        assert str(error) == "IPC failed"
        assert error.command == "wallpaper"
        assert error.exit_code == 2

    def test_ipc_error_raise(self):
        """Test raising HyprpaperIPCError."""
        with pytest.raises(HyprpaperIPCError) as exc_info:
            raise HyprpaperIPCError("IPC failed", command="preload", exit_code=1)
        assert "IPC failed" in str(exc_info.value)
        assert exc_info.value.command == "preload"
        assert exc_info.value.exit_code == 1


class TestWallpaperNotFoundError:
    def test_wallpaper_not_found_error_creation(self):
        """Test WallpaperNotFoundError creation."""
        error = WallpaperNotFoundError("Wallpaper not found: /test/wp.jpg")
        assert "not found" in str(error)
        assert isinstance(error, HyprpaperError)

    def test_wallpaper_not_found_error_raise(self):
        """Test raising WallpaperNotFoundError."""
        with pytest.raises(WallpaperNotFoundError) as exc_info:
            raise WallpaperNotFoundError("Wallpaper not found")
        assert "not found" in str(exc_info.value)


class TestMonitorNotFoundError:
    def test_monitor_not_found_error_creation(self):
        """Test MonitorNotFoundError creation."""
        error = MonitorNotFoundError("Monitor not found: DP-1")
        assert "not found" in str(error)
        assert isinstance(error, HyprpaperError)

    def test_monitor_not_found_error_raise(self):
        """Test raising MonitorNotFoundError."""
        with pytest.raises(MonitorNotFoundError) as exc_info:
            raise MonitorNotFoundError("Monitor not found")
        assert "not found" in str(exc_info.value)


class TestWallpaperNotLoadedError:
    def test_wallpaper_not_loaded_error_creation(self):
        """Test WallpaperNotLoadedError creation."""
        error = WallpaperNotLoadedError("Wallpaper not loaded: /test/wp.jpg")
        assert "not loaded" in str(error)
        assert isinstance(error, HyprpaperError)

    def test_wallpaper_not_loaded_error_raise(self):
        """Test raising WallpaperNotLoadedError."""
        with pytest.raises(WallpaperNotLoadedError) as exc_info:
            raise WallpaperNotLoadedError("Wallpaper not loaded")
        assert "not loaded" in str(exc_info.value)


class TestWallpaperTooLargeError:
    def test_wallpaper_too_large_error_basic(self):
        """Test WallpaperTooLargeError with basic message."""
        error = WallpaperTooLargeError("Wallpaper too large")
        assert str(error) == "Wallpaper too large"
        assert error.wallpaper_size_mb is None
        assert error.max_allowed_mb is None
        assert isinstance(error, HyprpaperError)

    def test_wallpaper_too_large_error_with_sizes(self):
        """Test WallpaperTooLargeError with size information."""
        error = WallpaperTooLargeError(
            "Wallpaper too large",
            wallpaper_size_mb=250.0,
            max_allowed_mb=200.0,
        )
        assert str(error) == "Wallpaper too large"
        assert error.wallpaper_size_mb == 250.0
        assert error.max_allowed_mb == 200.0

    def test_wallpaper_too_large_error_raise(self):
        """Test raising WallpaperTooLargeError."""
        with pytest.raises(WallpaperTooLargeError) as exc_info:
            raise WallpaperTooLargeError(
                "Wallpaper too large",
                wallpaper_size_mb=300.0,
                max_allowed_mb=200.0,
            )
        assert "too large" in str(exc_info.value)
        assert exc_info.value.wallpaper_size_mb == 300.0
        assert exc_info.value.max_allowed_mb == 200.0


class TestExceptionHierarchy:
    def test_all_exceptions_inherit_from_hyprpaper_error(self):
        """Test that all exceptions inherit from HyprpaperError."""
        assert issubclass(HyprpaperNotRunningError, HyprpaperError)
        assert issubclass(HyprpaperIPCError, HyprpaperError)
        assert issubclass(WallpaperNotFoundError, HyprpaperError)
        assert issubclass(MonitorNotFoundError, HyprpaperError)
        assert issubclass(WallpaperNotLoadedError, HyprpaperError)
        assert issubclass(WallpaperTooLargeError, HyprpaperError)

    def test_catch_base_exception(self):
        """Test catching specific exceptions with base exception."""
        with pytest.raises(HyprpaperError):
            raise HyprpaperNotRunningError("Test")

        with pytest.raises(HyprpaperError):
            raise WallpaperNotFoundError("Test")

        with pytest.raises(HyprpaperError):
            raise WallpaperTooLargeError("Test")


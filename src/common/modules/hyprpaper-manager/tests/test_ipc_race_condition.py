"""Tests for IPC race condition fixes."""

from unittest.mock import Mock, patch

import pytest

from hyprpaper_manager.core.exceptions import (
    HyprpaperIPCError,
    HyprpaperNotRunningError,
)
from hyprpaper_manager.ipc.client import HyprpaperIPC


@pytest.fixture
def ipc():
    """Create IPC client with test settings."""
    return HyprpaperIPC(
        timeout=5,
        retry_attempts=3,
        retry_delay=0.1,  # Faster for tests
        startup_wait=1.0,
    )


class TestSocketReadiness:
    """Test socket readiness checking."""

    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_is_ready_when_socket_ready(self, mock_run, ipc):
        """Test is_ready returns True when socket is ready."""
        mock_run.side_effect = [
            Mock(returncode=0),  # initial is_running check
            Mock(returncode=0),  # is_running check in loop
            Mock(returncode=0, stdout=""),  # listloaded check
        ]

        assert ipc.is_ready(max_wait=1.0) is True
        assert mock_run.call_count == 3

    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_is_ready_when_process_not_running(self, mock_run, ipc):
        """Test is_ready returns False when process not running."""
        mock_run.return_value = Mock(returncode=1)  # is_running returns False

        assert ipc.is_ready(max_wait=1.0) is False
        assert mock_run.call_count == 1  # Only is_running check

    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    @patch("hyprpaper_manager.ipc.client.time.sleep")
    def test_is_ready_waits_for_socket(self, mock_sleep, mock_run, ipc):
        """Test is_ready waits for socket to become ready."""
        # First attempt: process running but socket not ready
        # Second attempt: socket ready
        mock_run.side_effect = [
            Mock(returncode=0),  # initial is_running check
            Mock(returncode=0),  # is_running check in loop (attempt 1)
            Mock(returncode=1),  # listloaded fails (socket not ready)
            Mock(returncode=0),  # is_running check in loop (attempt 2)
            Mock(returncode=0),  # listloaded succeeds (socket ready)
        ]

        assert ipc.is_ready(max_wait=1.0) is True
        assert mock_run.call_count == 5
        assert mock_sleep.call_count >= 1  # Should have slept between attempts

    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    @patch("hyprpaper_manager.ipc.client.time.sleep")
    def test_is_ready_timeout(self, mock_sleep, mock_run, ipc):
        """Test is_ready returns False after timeout."""
        # Return failure for all listloaded attempts
        mock_run.return_value = Mock(returncode=1)

        # Use very short timeout for test
        assert ipc.is_ready(max_wait=0.2) is False

    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    @patch("hyprpaper_manager.ipc.client.time.sleep")
    def test_is_ready_process_dies_during_wait(
        self, mock_sleep, mock_run, ipc
    ):
        """Test is_ready detects when process dies during wait."""
        mock_run.side_effect = [
            Mock(returncode=0),  # initial is_running check (process alive)
            Mock(returncode=0),  # is_running check in loop (attempt 1)
            Mock(returncode=1),  # listloaded fails (socket not ready)
            Mock(returncode=1),  # is_running check in loop (process died!)
        ]

        # Should return False immediately when process dies
        assert ipc.is_ready(max_wait=1.0) is False
        # Should not wait full timeout - exits early when process dies
        assert mock_run.call_count == 4


class TestRetryLogic:
    """Test automatic retry logic."""

    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_running")
    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_ready")
    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_execute_succeeds_first_try(
        self, mock_run, mock_is_ready, mock_is_running, ipc
    ):
        """Test command succeeds on first attempt."""
        mock_is_running.return_value = True
        mock_is_ready.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="ok")

        result = ipc._execute("preload", "/test/wallpaper.png")
        assert result == "ok"
        # Called once for the actual command
        assert mock_run.call_count == 1

    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_running")
    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_ready")
    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    @patch("hyprpaper_manager.ipc.client.time.sleep")
    def test_execute_retries_on_failure(
        self, mock_sleep, mock_run, mock_is_ready, mock_is_running, ipc
    ):
        """Test command retries on transient failure."""
        from subprocess import CalledProcessError

        mock_is_running.return_value = True
        mock_is_ready.return_value = True
        mock_run.side_effect = [
            CalledProcessError(1, "cmd", stderr="temporary error"),
            Mock(returncode=0, stdout="ok"),
        ]

        result = ipc._execute("preload", "/test/wallpaper.png")
        assert result == "ok"
        assert mock_sleep.call_count >= 1  # Should have slept between retries

    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_running")
    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_ready")
    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    @patch("hyprpaper_manager.ipc.client.time.sleep")
    def test_execute_fails_after_max_retries(
        self, mock_sleep, mock_run, mock_is_ready, mock_is_running, ipc
    ):
        """Test command fails after max retries."""
        from subprocess import CalledProcessError

        mock_is_running.return_value = True
        mock_is_ready.return_value = True
        mock_run.side_effect = [
            CalledProcessError(1, "cmd", stderr="error 1"),
            CalledProcessError(1, "cmd", stderr="error 2"),
            CalledProcessError(1, "cmd", stderr="error 3"),
        ]

        with pytest.raises(HyprpaperIPCError) as exc_info:
            ipc._execute("preload", "/test/wallpaper.png")

        assert "Command failed" in str(exc_info.value)
        assert mock_sleep.call_count >= 2  # Should have slept between retries

    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_running")
    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_ready")
    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_execute_no_retry_when_disabled(
        self, mock_run, mock_is_ready, mock_is_running, ipc
    ):
        """Test command doesn't retry when retry=False."""
        from subprocess import CalledProcessError

        mock_is_running.return_value = True
        mock_is_ready.return_value = True
        mock_run.side_effect = CalledProcessError(1, "cmd", stderr="error")

        with pytest.raises(HyprpaperIPCError):
            ipc._execute("preload", "/test/wallpaper.png", retry=False)

        # Should only try once
        assert mock_run.call_count == 1


class TestImprovedErrorMessages:
    """Test improved error messages."""

    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_error_message_when_socket_not_ready(self, mock_run, ipc):
        """Test error message when socket is not ready."""
        mock_run.side_effect = [
            Mock(returncode=0),  # is_running
            Mock(returncode=1),  # is_ready fails (socket not ready)
            Mock(returncode=1),
            Mock(returncode=1),
        ]

        with pytest.raises(HyprpaperIPCError) as exc_info:
            ipc._execute("preload", "/test/wallpaper.png")

        error_msg = str(exc_info.value)
        assert (
            "socket" in error_msg.lower() or "not ready" in error_msg.lower()
        )

    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_error_message_when_process_not_running(self, mock_run, ipc):
        """Test error message when process is not running."""
        mock_run.return_value = Mock(returncode=1)  # is_running returns False

        with pytest.raises(HyprpaperNotRunningError) as exc_info:
            ipc._execute("preload", "/test/wallpaper.png")

        error_msg = str(exc_info.value)
        assert "not running" in error_msg.lower()
        assert "hyprpaper &" in error_msg  # Should suggest how to start

    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_running")
    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_ready")
    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_error_message_with_stderr(
        self, mock_run, mock_is_ready, mock_is_running, ipc
    ):
        """Test error message includes stderr when available."""
        from subprocess import CalledProcessError

        mock_is_running.return_value = True
        mock_is_ready.return_value = True
        mock_run.side_effect = CalledProcessError(
            1, "cmd", stderr="specific error message"
        )

        with pytest.raises(HyprpaperIPCError) as exc_info:
            ipc._execute("preload", "/test/wallpaper.png")

        error_msg = str(exc_info.value)
        assert "specific error message" in error_msg


class TestPerCommandTimeout:
    """Test per-command timeout overrides."""

    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_ready")
    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_custom_timeout_used(self, mock_run, mock_is_ready, ipc):
        """Test custom timeout is used when specified."""
        mock_is_ready.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="ok")

        ipc._execute("preload", "/test/wallpaper.png", timeout=10)

        # Check that timeout=10 was passed to subprocess.run
        assert mock_run.call_args[1]["timeout"] == 10

    @patch("hyprpaper_manager.ipc.client.HyprpaperIPC.is_ready")
    @patch("hyprpaper_manager.ipc.client.subprocess.run")
    def test_default_timeout_used(self, mock_run, mock_is_ready, ipc):
        """Test default timeout is used when not specified."""
        mock_is_ready.return_value = True
        mock_run.return_value = Mock(returncode=0, stdout="ok")

        ipc._execute("preload", "/test/wallpaper.png")

        # Check that default timeout was used
        assert mock_run.call_args[1]["timeout"] == ipc.timeout

    def test_public_methods_accept_timeout(self, ipc):
        """Test that public methods accept timeout parameter."""
        # Just verify the signature - actual execution tested elsewhere
        assert "timeout" in ipc.preload.__code__.co_varnames
        assert "timeout" in ipc.wallpaper.__code__.co_varnames
        assert "timeout" in ipc.unload.__code__.co_varnames
        assert "timeout" in ipc.reload.__code__.co_varnames
        assert "timeout" in ipc.listloaded.__code__.co_varnames
        assert "timeout" in ipc.listactive.__code__.co_varnames

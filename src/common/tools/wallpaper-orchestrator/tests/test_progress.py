"""Test progress tracking in wallpaper orchestrator."""

import contextlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from wallpaper_orchestrator import WallpaperOrchestrator


def test_progress_callback_parameter():
    """Test that WallpaperOrchestrator accepts progress_callback parameter."""
    callback = MagicMock()
    orchestrator = WallpaperOrchestrator(progress_callback=callback)

    assert orchestrator._progress_callback is callback


def test_status_methods_before_execution():
    """Test status methods return correct values before execution."""
    orchestrator = WallpaperOrchestrator()

    status = orchestrator.get_status()
    assert status["progress"] == 0.0
    assert status["current_step"] is None
    assert status["is_running"] is False

    assert orchestrator.is_running() is False
    assert orchestrator.get_current_step() is None


def test_backward_compatibility():
    """Test that orchestrator works without progress callback."""
    # Should not raise any errors
    orchestrator = WallpaperOrchestrator()

    # Verify callback is None
    assert orchestrator._progress_callback is None

    # Verify status methods work
    assert orchestrator.get_status() is not None
    assert orchestrator.is_running() is False


def test_pipeline_receives_callback():
    """Test that progress callback is passed to Pipeline."""
    callback = MagicMock()
    orchestrator = WallpaperOrchestrator(progress_callback=callback)

    # Mock the pipeline and its dependencies
    with patch(
        "wallpaper_orchestrator.orchestrator.Pipeline"
    ) as mock_pipeline:
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        # Mock the pipeline run to return a context with no errors
        mock_context = MagicMock()
        mock_context.errors = []
        mock_pipeline_instance.run.return_value = mock_context

        # Create a test wallpaper path (doesn't need to exist for this test)
        test_wallpaper = Path("/tmp/test_wallpaper.png")

        # Mock the file existence check
        # We expect some errors due to mocking, but we just want
        # to verify the Pipeline was created with the callback
        with (
            patch.object(Path, "exists", return_value=True),
            contextlib.suppress(Exception),
        ):
            orchestrator.process(test_wallpaper)

        # Verify Pipeline was called with the callback
        mock_pipeline.assert_called_once()
        call_args = mock_pipeline.call_args

        # The third argument should be the progress callback
        assert len(call_args[0]) >= 3 or "progress_callback" in call_args[1]
        if len(call_args[0]) >= 3:
            assert call_args[0][2] is callback
        else:
            assert call_args[1].get("progress_callback") is callback


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

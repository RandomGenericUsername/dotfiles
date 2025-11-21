"""Tests for state manager."""

import json
import pytest
from pathlib import Path
from rofi_colorscheme_viewer.viewer.state_manager import StateManager


class TestStateManager:
    """Test state manager."""

    def test_init_creates_state_file(self, tmp_path):
        """Test that initialization creates state file."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file, default_format="hex")

        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert data["current_format"] == "hex"

    def test_init_with_existing_state_file(self, mock_state_file):
        """Test initialization with existing state file."""
        manager = StateManager(mock_state_file, default_format="hex")

        assert manager.get_current_format() == "hex"

    def test_get_current_format(self, tmp_path):
        """Test getting current format."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file, default_format="rgb")

        assert manager.get_current_format() == "rgb"

    def test_set_format(self, tmp_path):
        """Test setting format."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file, default_format="hex")

        manager.set_format("rgb")
        assert manager.get_current_format() == "rgb"

        # Verify persistence
        data = json.loads(state_file.read_text())
        assert data["current_format"] == "rgb"

    def test_cycle_format(self, tmp_path):
        """Test cycling through formats."""
        state_file = tmp_path / "state.json"
        manager = StateManager(
            state_file,
            default_format="hex",
            available_formats=["hex", "rgb", "json"]
        )

        # Start with hex
        assert manager.get_current_format() == "hex"

        # Cycle to rgb
        result = manager.cycle_format()
        assert result == "rgb"
        assert manager.get_current_format() == "rgb"

        # Cycle to json
        result = manager.cycle_format()
        assert result == "json"
        assert manager.get_current_format() == "json"

        # Cycle back to hex
        result = manager.cycle_format()
        assert result == "hex"
        assert manager.get_current_format() == "hex"

    def test_cycle_format_persistence(self, tmp_path):
        """Test that cycling persists to file."""
        state_file = tmp_path / "state.json"
        manager = StateManager(
            state_file,
            default_format="hex",
            available_formats=["hex", "rgb", "json"]
        )

        manager.cycle_format()  # hex -> rgb

        # Create new manager instance
        manager2 = StateManager(
            state_file,
            default_format="hex",
            available_formats=["hex", "rgb", "json"]
        )

        # Should remember rgb
        assert manager2.get_current_format() == "rgb"

    def test_set_invalid_format(self, tmp_path):
        """Test setting invalid format."""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file, default_format="hex")

        # Should not change format
        manager.set_format("invalid")
        assert manager.get_current_format() == "hex"

    def test_custom_available_formats(self, tmp_path):
        """Test with custom available formats."""
        state_file = tmp_path / "state.json"
        manager = StateManager(
            state_file,
            default_format="hex",
            available_formats=["hex", "rgb"]  # Only hex and rgb
        )

        assert manager.get_current_format() == "hex"

        manager.cycle_format()
        assert manager.get_current_format() == "rgb"

        manager.cycle_format()
        assert manager.get_current_format() == "hex"  # Wraps back

    def test_state_file_corruption_recovery(self, tmp_path):
        """Test recovery from corrupted state file."""
        state_file = tmp_path / "state.json"
        state_file.write_text("invalid json{")

        # Should recover with default format
        manager = StateManager(state_file, default_format="hex")
        assert manager.get_current_format() == "hex"

        # Should have fixed the file
        data = json.loads(state_file.read_text())
        assert data["current_format"] == "hex"

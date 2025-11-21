"""Tests for manager client."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from rofi_wallpaper_selector.utils.manager_client import ManagerClient


class TestManagerClient:
    """Test manager client."""

    def test_init_raises_when_cli_not_found(self, tmp_path):
        """Test that init raises FileNotFoundError when CLI doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Manager CLI not found"):
            ManagerClient(tmp_path)

    def test_init_succeeds_when_cli_exists(self, tmp_path):
        """Test that init succeeds when CLI exists."""
        # Create mock CLI
        venv_bin = tmp_path / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        cli_path = venv_bin / "dotfiles-manager"
        cli_path.touch()

        client = ManagerClient(tmp_path)

        assert client.manager_path == tmp_path
        assert client.manager_cli == cli_path

    @patch("subprocess.run")
    def test_get_current_wallpaper_parses_table(self, mock_run, tmp_path):
        """Test that get_current_wallpaper parses table output correctly."""
        # Setup
        venv_bin = tmp_path / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        (venv_bin / "dotfiles-manager").touch()
        client = ManagerClient(tmp_path)

        # Mock subprocess output
        mock_run.return_value = Mock(
            stdout="│ Monitor │ Wallpaper │ Last Changed │\n"
                   "│ DP-1    │ /path/to/wallpaper.png │ 2024-01-01 │\n"
        )

        result = client.get_current_wallpaper("DP-1")

        assert result == Path("/path/to/wallpaper.png")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_current_wallpaper_returns_none_when_not_set(self, mock_run, tmp_path):
        """Test that get_current_wallpaper returns None when wallpaper not set."""
        # Setup
        venv_bin = tmp_path / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        (venv_bin / "dotfiles-manager").touch()
        client = ManagerClient(tmp_path)

        # Mock subprocess output
        mock_run.return_value = Mock(
            stdout="│ Monitor │ Wallpaper │ Last Changed │\n"
                   "│ DP-1    │ Not set   │ Never │\n"
        )

        result = client.get_current_wallpaper("DP-1")

        assert result is None

    @patch("subprocess.run")
    def test_change_wallpaper_calls_cli_with_correct_args(self, mock_run, tmp_path):
        """Test that change_wallpaper calls CLI with correct arguments."""
        # Setup
        venv_bin = tmp_path / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        cli_path = venv_bin / "dotfiles-manager"
        cli_path.touch()
        client = ManagerClient(tmp_path)

        wallpaper_path = Path("/path/to/wallpaper.png")

        client.change_wallpaper(
            wallpaper_path,
            "DP-1",
            generate_colorscheme=True,
            generate_effects=True
        )

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]

        assert str(cli_path) in call_args
        assert "change-wallpaper" in call_args
        assert str(wallpaper_path) in call_args
        assert "--monitor" in call_args
        assert "DP-1" in call_args
        assert "--colorscheme" in call_args
        assert "--effects" in call_args

    @patch("subprocess.run")
    def test_change_wallpaper_with_no_colorscheme(self, mock_run, tmp_path):
        """Test change_wallpaper with generate_colorscheme=False."""
        # Setup
        venv_bin = tmp_path / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        (venv_bin / "dotfiles-manager").touch()
        client = ManagerClient(tmp_path)

        client.change_wallpaper(
            Path("/path/to/wallpaper.png"),
            "DP-1",
            generate_colorscheme=False,
            generate_effects=False
        )

        call_args = mock_run.call_args[0][0]
        assert "--no-colorscheme" in call_args
        assert "--no-effects" in call_args

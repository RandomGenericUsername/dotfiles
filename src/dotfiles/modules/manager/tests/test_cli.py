"""Tests for CLI interface."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from dotfiles_manager.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Dotfiles manager CLI" in result.stdout


def test_status_command() -> None:
    """Test status command."""
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Manager Configuration" in result.stdout
    assert "Data Directory" in result.stdout
    assert "Debug Mode" in result.stdout


def test_status_command_verbose() -> None:
    """Test status command with verbose flag."""
    result = runner.invoke(app, ["status", "--verbose"])
    assert result.exit_code == 0
    assert "Manager Configuration" in result.stdout
    assert "Manager Details" in result.stdout


def test_info_command() -> None:
    """Test info command."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Dotfiles Manager" in result.stdout
    assert "Usage:" in result.stdout


def test_init_command_default() -> None:
    """Test init command with default settings."""
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Manager initialized" in result.stdout


def test_init_command_custom_data_dir(tmp_path: Path) -> None:
    """Test init command with custom data directory."""
    data_dir = tmp_path / "custom_data"
    result = runner.invoke(app, ["init", "--data-dir", str(data_dir)])
    assert result.exit_code == 0
    assert "Manager initialized" in result.stdout
    assert str(data_dir) in result.stdout


def test_init_command_with_debug(tmp_path: Path) -> None:
    """Test init command with debug flag."""
    data_dir = tmp_path / "debug_data"
    result = runner.invoke(
        app, ["init", "--data-dir", str(data_dir), "--debug"]
    )
    assert result.exit_code == 0
    assert "Manager initialized" in result.stdout
    assert "Debug mode enabled" in result.stdout


def test_status_command_error_handling() -> None:
    """Test status command error handling."""
    with patch("dotfiles_manager.cli.Manager") as mock_manager_class:
        mock_manager_class.side_effect = Exception("Test error")
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 1
        assert "Error: Test error" in result.stdout


def test_init_command_error_handling() -> None:
    """Test init command error handling."""
    with patch("dotfiles_manager.cli.Manager") as mock_manager_class:
        mock_manager_class.side_effect = Exception("Init error")
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 1
        assert "Error initializing manager" in result.stdout

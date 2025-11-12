"""Tests for Manager class."""

from dotfiles_manager import Manager, ManagerConfig


def test_manager_initialization() -> None:
    """Test Manager can be initialized."""
    manager = Manager()
    assert manager is not None
    assert manager.config is not None


def test_manager_with_custom_config() -> None:
    """Test Manager with custom configuration."""
    config = ManagerConfig(debug=True)
    manager = Manager(config=config)
    assert manager.config.debug is True


def test_manager_context_manager() -> None:
    """Test Manager as context manager."""
    with Manager() as manager:
        assert manager is not None


def test_manager_close() -> None:
    """Test Manager close method."""
    manager = Manager()
    manager.close()  # Should not raise

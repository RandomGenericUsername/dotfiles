"""Test container initialization."""

import pytest

from dotfiles_manager.container import Container


def test_container_initialization():
    """Test that container can be initialized."""
    container = Container.initialize()

    assert container is not None
    assert container.config is not None
    assert container.system_state is not None
    assert container.wallpaper_orchestrator is not None


def test_container_services():
    """Test that services can be retrieved from container."""
    container = Container.initialize()

    # Test service retrieval
    wallpaper_service = container.wallpaper_service()
    wlogout_service = container.wlogout_service()

    assert wallpaper_service is not None
    assert wlogout_service is not None


def test_container_repositories():
    """Test that repositories can be retrieved from container."""
    container = Container.initialize()

    # Test repository retrieval
    system_attrs_repo = container.system_attributes_repo()
    wallpaper_state_repo = container.wallpaper_state_repo()

    assert system_attrs_repo is not None
    assert wallpaper_state_repo is not None


def test_container_hook_registry():
    """Test that hook registry is initialized with hooks."""
    container = Container.initialize()

    # Test hook registry
    hook_registry = container.hook_registry()

    assert hook_registry is not None
    # Verify wlogout hook is registered
    assert "wlogout_icons" in hook_registry._hooks

"""Pytest configuration and fixtures for socket module tests."""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_socket_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for socket files.

    Yields:
        Path to temporary directory

    Cleanup:
        Removes the directory after test completes
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="socket_test_"))
    try:
        yield temp_dir
    finally:
        # Clean up socket files and directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@pytest.fixture
def event_name() -> str:
    """Provide a test event name.

    Returns:
        Test event name
    """
    return "test_event"


@pytest.fixture
def tcp_host() -> str:
    """Provide a test TCP host.

    Returns:
        Localhost IP address
    """
    return "127.0.0.1"


@pytest.fixture
def tcp_port_range() -> tuple[int, int]:
    """Provide a test TCP port range.

    Returns:
        Tuple of (start_port, end_port)
    """
    return (9000, 9100)

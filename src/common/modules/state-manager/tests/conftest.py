"""Shared fixtures for state manager tests."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dotfiles_state_manager import SQLiteBackend, StateManager

try:
    from dotfiles_state_manager import RedisBackend

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    RedisBackend = None


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()
    # Also cleanup WAL files
    wal_path = db_path.with_suffix(".db-wal")
    if wal_path.exists():
        wal_path.unlink()
    shm_path = db_path.with_suffix(".db-shm")
    if shm_path.exists():
        shm_path.unlink()


@pytest.fixture
def sqlite_backend(temp_db):
    """Create a SQLite backend for testing."""
    backend = SQLiteBackend(db_path=temp_db)
    yield backend
    backend.close()


@pytest.fixture
def state_manager(sqlite_backend):
    """Create a state manager with SQLite backend."""
    manager = StateManager(backend=sqlite_backend)
    yield manager
    manager.close()


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client for testing."""
    mock = MagicMock()
    mock.ping.return_value = True
    mock.set.return_value = True
    mock.get.return_value = None
    mock.delete.return_value = 1
    mock.exists.return_value = 0
    mock.keys.return_value = []
    mock.hset.return_value = 1
    mock.hget.return_value = None
    mock.hgetall.return_value = {}
    mock.hdel.return_value = 1
    mock.hexists.return_value = False
    mock.lpush.return_value = 1
    mock.rpush.return_value = 1
    mock.lrange.return_value = []
    mock.llen.return_value = 0
    mock.lpop.return_value = None
    mock.rpop.return_value = None
    mock.sadd.return_value = 1
    mock.smembers.return_value = set()
    mock.sismember.return_value = False
    mock.srem.return_value = 1
    mock.scard.return_value = 0
    mock.expire.return_value = True
    mock.ttl.return_value = -2
    mock.persist.return_value = True
    mock.flushdb.return_value = True
    mock.close.return_value = None
    return mock


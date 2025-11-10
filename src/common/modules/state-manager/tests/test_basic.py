"""Basic tests for state manager."""

import tempfile
from pathlib import Path

import pytest

from dotfiles_state_manager import SQLiteBackend, StateManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


def test_state_manager_creation(temp_db):
    """Test creating a state manager."""
    backend = SQLiteBackend(db_path=temp_db)
    state = StateManager(backend=backend)
    
    assert state is not None
    state.close()


def test_key_value_operations(temp_db):
    """Test basic key-value operations."""
    backend = SQLiteBackend(db_path=temp_db)
    state = StateManager(backend=backend)
    
    # Set and get
    state.set("test_key", "test_value")
    assert state.get("test_key") == "test_value"
    
    # Exists
    assert state.exists("test_key")
    assert not state.exists("nonexistent_key")
    
    # Delete
    assert state.delete("test_key")
    assert not state.exists("test_key")
    assert state.get("test_key") is None
    
    state.close()


def test_hash_operations(temp_db):
    """Test hash operations."""
    backend = SQLiteBackend(db_path=temp_db)
    state = StateManager(backend=backend)
    
    # Set fields
    state.hset("user:1", "name", "John")
    state.hset("user:1", "email", "john@example.com")
    state.hset("user:1", "age", 30)
    
    # Get field
    assert state.hget("user:1", "name") == "John"
    assert state.hget("user:1", "email") == "john@example.com"
    assert state.hget("user:1", "age") == 30
    
    # Get all fields
    user = state.hgetall("user:1")
    assert user == {"name": "John", "email": "john@example.com", "age": 30}
    
    # Field exists
    assert state.hexists("user:1", "name")
    assert not state.hexists("user:1", "nonexistent")
    
    # Delete field
    assert state.hdel("user:1", "age")
    assert not state.hexists("user:1", "age")
    
    state.close()


def test_list_operations(temp_db):
    """Test list operations."""
    backend = SQLiteBackend(db_path=temp_db)
    state = StateManager(backend=backend)
    
    # Push operations
    state.rpush("tasks", "task1")
    state.rpush("tasks", "task2")
    state.lpush("tasks", "task0")
    
    # Get range
    tasks = state.lrange("tasks", 0, -1)
    assert tasks == ["task0", "task1", "task2"]
    
    # Length
    assert state.llen("tasks") == 3
    
    # Pop operations
    assert state.lpop("tasks") == "task0"
    assert state.rpop("tasks") == "task2"
    assert state.llen("tasks") == 1
    
    state.close()


def test_set_operations(temp_db):
    """Test set operations."""
    backend = SQLiteBackend(db_path=temp_db)
    state = StateManager(backend=backend)
    
    # Add members
    added = state.sadd("tags", "python", "redis", "sqlite")
    assert added == 3
    
    # Add duplicate (should not add)
    added = state.sadd("tags", "python")
    assert added == 0
    
    # Get members
    tags = state.smembers("tags")
    assert tags == {"python", "redis", "sqlite"}
    
    # Is member
    assert state.sismember("tags", "python")
    assert not state.sismember("tags", "java")
    
    # Cardinality
    assert state.scard("tags") == 3
    
    # Remove members
    removed = state.srem("tags", "redis", "sqlite")
    assert removed == 2
    assert state.scard("tags") == 1
    
    state.close()


def test_ttl_operations(temp_db):
    """Test TTL/expiration operations."""
    backend = SQLiteBackend(db_path=temp_db)
    state = StateManager(backend=backend)
    
    # Set key with expiration
    state.set("temp_key", "temp_value")
    assert state.expire("temp_key", 3600)
    
    # Check TTL
    ttl = state.ttl("temp_key")
    assert ttl is not None
    assert ttl > 0
    assert ttl <= 3600
    
    # Persist (remove expiration)
    assert state.persist("temp_key")
    assert state.ttl("temp_key") is None
    
    # TTL on nonexistent key
    assert state.ttl("nonexistent") == -2
    
    state.close()


def test_context_manager(temp_db):
    """Test context manager support."""
    backend = SQLiteBackend(db_path=temp_db)
    
    with StateManager(backend=backend) as state:
        state.set("key", "value")
        assert state.get("key") == "value"
    
    # State should be closed after context


def test_keys_pattern_matching(temp_db):
    """Test keys with pattern matching."""
    backend = SQLiteBackend(db_path=temp_db)
    state = StateManager(backend=backend)
    
    # Set multiple keys
    state.set("user:1", "John")
    state.set("user:2", "Jane")
    state.set("post:1", "Hello")
    state.set("post:2", "World")
    
    # Get all keys
    all_keys = state.keys()
    assert len(all_keys) == 4
    
    # Get keys with pattern
    user_keys = state.keys("user:*")
    assert len(user_keys) == 2
    assert "user:1" in user_keys
    assert "user:2" in user_keys
    
    post_keys = state.keys("post:*")
    assert len(post_keys) == 2
    
    state.close()


def test_cleanup_expired(temp_db):
    """Test cleanup of expired keys."""
    backend = SQLiteBackend(db_path=temp_db)
    state = StateManager(backend=backend)
    
    # Set keys with very short expiration
    state.set("key1", "value1")
    state.expire("key1", 1)
    
    state.set("key2", "value2")
    state.expire("key2", 1)
    
    state.set("key3", "value3")  # No expiration
    
    # Wait for expiration
    import time
    time.sleep(2)
    
    # Cleanup
    removed = state.cleanup_expired()
    assert removed >= 2
    
    # Check that expired keys are gone
    assert not state.exists("key1")
    assert not state.exists("key2")
    assert state.exists("key3")
    
    state.close()


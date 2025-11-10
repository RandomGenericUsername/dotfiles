"""Tests for StateManager wrapper class."""

from dotfiles_state_manager import StateManager


class TestStateManagerInitialization:
    """Tests for StateManager initialization."""

    def test_create_with_backend(self, sqlite_backend):
        """Test creating state manager with backend."""
        manager = StateManager(backend=sqlite_backend)
        assert manager._backend == sqlite_backend
        manager.close()

    def test_context_manager_support(self, sqlite_backend):
        """Test context manager support."""
        with StateManager(backend=sqlite_backend) as manager:
            manager.set("key", "value")
            assert manager.get("key") == "value"
        # Manager should be closed after context

    def test_context_manager_closes_on_exception(self, sqlite_backend):
        """Test context manager closes even on exception."""
        try:
            with StateManager(backend=sqlite_backend) as manager:
                manager.set("key", "value")
                raise ValueError("Test exception")
        except ValueError:
            pass
        # Manager should still be closed


class TestStateManagerKeyValueOperations:
    """Tests for StateManager key-value operations."""

    def test_set_and_get(self, state_manager):
        """Test set and get operations."""
        state_manager.set("key", "value")
        assert state_manager.get("key") == "value"

    def test_get_nonexistent_returns_none(self, state_manager):
        """Test get on nonexistent key returns None."""
        assert state_manager.get("nonexistent") is None

    def test_get_with_default(self, state_manager):
        """Test get with default value."""
        assert state_manager.get("nonexistent", "default") == "default"

    def test_delete(self, state_manager):
        """Test delete operation."""
        state_manager.set("key", "value")
        assert state_manager.delete("key")
        assert not state_manager.exists("key")

    def test_delete_nonexistent_returns_false(self, state_manager):
        """Test delete on nonexistent key returns False."""
        assert not state_manager.delete("nonexistent")

    def test_exists(self, state_manager):
        """Test exists operation."""
        state_manager.set("key", "value")
        assert state_manager.exists("key")
        assert not state_manager.exists("nonexistent")

    def test_keys_without_pattern(self, state_manager):
        """Test keys without pattern."""
        state_manager.set("key1", "value1")
        state_manager.set("key2", "value2")
        keys = state_manager.keys()
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys

    def test_keys_with_pattern(self, state_manager):
        """Test keys with pattern."""
        state_manager.set("user:1", "John")
        state_manager.set("user:2", "Jane")
        state_manager.set("post:1", "Hello")

        user_keys = state_manager.keys("user:*")
        assert len(user_keys) == 2
        assert "user:1" in user_keys
        assert "user:2" in user_keys


class TestStateManagerHashOperations:
    """Tests for StateManager hash operations."""

    def test_hset_and_hget(self, state_manager):
        """Test hset and hget operations."""
        state_manager.hset("hash", "field", "value")
        assert state_manager.hget("hash", "field") == "value"

    def test_hget_nonexistent_returns_none(self, state_manager):
        """Test hget on nonexistent field returns None."""
        assert state_manager.hget("hash", "nonexistent") is None

    def test_hget_with_default(self, state_manager):
        """Test hget with default value."""
        assert (
            state_manager.hget("hash", "nonexistent", "default") == "default"
        )

    def test_hgetall(self, state_manager):
        """Test hgetall operation."""
        state_manager.hset("hash", "field1", "value1")
        state_manager.hset("hash", "field2", "value2")

        result = state_manager.hgetall("hash")
        assert result == {"field1": "value1", "field2": "value2"}

    def test_hgetall_nonexistent_returns_empty_dict(self, state_manager):
        """Test hgetall on nonexistent hash returns empty dict."""
        assert state_manager.hgetall("nonexistent") == {}

    def test_hdel(self, state_manager):
        """Test hdel operation."""
        state_manager.hset("hash", "field", "value")
        assert state_manager.hdel("hash", "field")
        assert not state_manager.hexists("hash", "field")

    def test_hdel_nonexistent_returns_false(self, state_manager):
        """Test hdel on nonexistent field returns False."""
        assert not state_manager.hdel("hash", "nonexistent")

    def test_hexists(self, state_manager):
        """Test hexists operation."""
        state_manager.hset("hash", "field", "value")
        assert state_manager.hexists("hash", "field")
        assert not state_manager.hexists("hash", "nonexistent")


class TestStateManagerListOperations:
    """Tests for StateManager list operations."""

    def test_lpush_and_rpush(self, state_manager):
        """Test lpush and rpush operations."""
        state_manager.rpush("list", "b")
        state_manager.lpush("list", "a")
        state_manager.rpush("list", "c")

        result = state_manager.lrange("list", 0, -1)
        assert result == ["a", "b", "c"]

    def test_lrange(self, state_manager):
        """Test lrange operation."""
        state_manager.rpush("list", "a")
        state_manager.rpush("list", "b")
        state_manager.rpush("list", "c")

        assert state_manager.lrange("list", 0, 1) == ["a", "b"]
        assert state_manager.lrange("list", 1, 2) == ["b", "c"]

    def test_lrange_nonexistent_returns_empty(self, state_manager):
        """Test lrange on nonexistent list returns empty list."""
        assert state_manager.lrange("nonexistent", 0, -1) == []

    def test_llen(self, state_manager):
        """Test llen operation."""
        state_manager.rpush("list", "a")
        state_manager.rpush("list", "b")
        assert state_manager.llen("list") == 2

    def test_llen_nonexistent_returns_zero(self, state_manager):
        """Test llen on nonexistent list returns 0."""
        assert state_manager.llen("nonexistent") == 0

    def test_lpop_and_rpop(self, state_manager):
        """Test lpop and rpop operations."""
        state_manager.rpush("list", "a")
        state_manager.rpush("list", "b")
        state_manager.rpush("list", "c")

        assert state_manager.lpop("list") == "a"
        assert state_manager.rpop("list") == "c"
        assert state_manager.llen("list") == 1

    def test_lpop_nonexistent_returns_none(self, state_manager):
        """Test lpop on nonexistent list returns None."""
        assert state_manager.lpop("nonexistent") is None

    def test_rpop_nonexistent_returns_none(self, state_manager):
        """Test rpop on nonexistent list returns None."""
        assert state_manager.rpop("nonexistent") is None


class TestStateManagerSetOperations:
    """Tests for StateManager set operations."""

    def test_sadd(self, state_manager):
        """Test sadd operation."""
        added = state_manager.sadd("set", "a", "b", "c")
        assert added == 3
        assert state_manager.scard("set") == 3

    def test_sadd_duplicate_returns_zero(self, state_manager):
        """Test sadd with duplicate returns 0."""
        state_manager.sadd("set", "a")
        added = state_manager.sadd("set", "a")
        assert added == 0

    def test_smembers(self, state_manager):
        """Test smembers operation."""
        state_manager.sadd("set", "a", "b", "c")
        members = state_manager.smembers("set")
        assert members == {"a", "b", "c"}

    def test_smembers_nonexistent_returns_empty_set(self, state_manager):
        """Test smembers on nonexistent set returns empty set."""
        assert state_manager.smembers("nonexistent") == set()

    def test_sismember(self, state_manager):
        """Test sismember operation."""
        state_manager.sadd("set", "a", "b")
        assert state_manager.sismember("set", "a")
        assert not state_manager.sismember("set", "c")

    def test_srem(self, state_manager):
        """Test srem operation."""
        state_manager.sadd("set", "a", "b", "c")
        removed = state_manager.srem("set", "a", "b")
        assert removed == 2
        assert state_manager.scard("set") == 1

    def test_srem_nonexistent_returns_zero(self, state_manager):
        """Test srem on nonexistent value returns 0."""
        removed = state_manager.srem("set", "nonexistent")
        assert removed == 0

    def test_scard(self, state_manager):
        """Test scard operation."""
        state_manager.sadd("set", "a", "b", "c")
        assert state_manager.scard("set") == 3

    def test_scard_nonexistent_returns_zero(self, state_manager):
        """Test scard on nonexistent set returns 0."""
        assert state_manager.scard("nonexistent") == 0


class TestStateManagerTTLOperations:
    """Tests for StateManager TTL operations."""

    def test_expire(self, state_manager):
        """Test expire operation."""
        state_manager.set("key", "value")
        assert state_manager.expire("key", 3600)
        ttl = state_manager.ttl("key")
        assert ttl is not None
        assert ttl > 0

    def test_expire_nonexistent_returns_false(self, state_manager):
        """Test expire on nonexistent key returns False."""
        assert not state_manager.expire("nonexistent", 3600)

    def test_ttl(self, state_manager):
        """Test ttl operation."""
        state_manager.set("key", "value")
        state_manager.expire("key", 3600)
        ttl = state_manager.ttl("key")
        assert ttl is not None
        assert 0 < ttl <= 3600

    def test_ttl_nonexistent_returns_minus_two(self, state_manager):
        """Test ttl on nonexistent key returns -2."""
        assert state_manager.ttl("nonexistent") == -2

    def test_ttl_no_expiration_returns_none(self, state_manager):
        """Test ttl on key without expiration returns None."""
        state_manager.set("key", "value")
        assert state_manager.ttl("key") is None

    def test_persist(self, state_manager):
        """Test persist operation."""
        state_manager.set("key", "value")
        state_manager.expire("key", 3600)
        assert state_manager.persist("key")
        assert state_manager.ttl("key") is None

    def test_persist_nonexistent_returns_false(self, state_manager):
        """Test persist on nonexistent key returns False."""
        assert not state_manager.persist("nonexistent")


class TestStateManagerMaintenanceOperations:
    """Tests for StateManager maintenance operations."""

    def test_cleanup_expired(self, state_manager):
        """Test cleanup_expired operation."""
        import time

        state_manager.set("key1", "value1")
        state_manager.expire("key1", 1)

        state_manager.set("key2", "value2")

        time.sleep(1.1)
        removed = state_manager.cleanup_expired()

        assert removed >= 1
        assert not state_manager.exists("key1")
        assert state_manager.exists("key2")

    def test_clear_all(self, state_manager):
        """Test clear_all operation."""
        state_manager.set("key", "value")
        state_manager.hset("hash", "field", "value")
        state_manager.rpush("list", "value")
        state_manager.sadd("set", "value")

        state_manager.clear_all()

        assert len(state_manager.keys()) == 0

    def test_close(self, sqlite_backend):
        """Test close operation."""
        manager = StateManager(backend=sqlite_backend)
        manager.set("key", "value")
        manager.close()
        # Backend should be closed

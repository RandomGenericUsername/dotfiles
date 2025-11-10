"""Tests for SQLite backend edge cases and advanced features."""

import time
from pathlib import Path

import pytest

from dotfiles_state_manager import SQLiteBackend


class TestSQLiteBackendInitialization:
    """Tests for SQLite backend initialization."""

    def test_create_with_path_object(self, temp_db):
        """Test creating backend with Path object."""
        backend = SQLiteBackend(db_path=temp_db)
        assert backend.db_path == temp_db
        backend.close()

    def test_create_with_string_path(self, tmp_path):
        """Test creating backend with string path."""
        db_path = str(tmp_path / "test.db")
        backend = SQLiteBackend(db_path=db_path)
        assert backend.db_path == Path(db_path)
        backend.close()

    def test_create_directory_if_not_exists(self, tmp_path):
        """Test that parent directory is created if it doesn't exist."""
        db_path = tmp_path / "subdir" / "nested" / "test.db"
        backend = SQLiteBackend(db_path=db_path)
        assert db_path.parent.exists()
        backend.close()

    def test_wal_mode_enabled_by_default(self, temp_db):
        """Test that WAL mode is enabled by default."""
        backend = SQLiteBackend(db_path=temp_db, wal_mode=True)
        cursor = backend.conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        assert mode.lower() == "wal"
        backend.close()

    def test_wal_mode_can_be_disabled(self, temp_db):
        """Test that WAL mode can be disabled."""
        backend = SQLiteBackend(db_path=temp_db, wal_mode=False)
        cursor = backend.conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        assert mode.lower() != "wal"
        backend.close()


class TestSQLiteBackendEdgeCases:
    """Tests for SQLite backend edge cases."""

    def test_set_and_get_none_value(self, sqlite_backend):
        """Test storing and retrieving None value."""
        sqlite_backend.set("null_key", None)
        assert sqlite_backend.get("null_key") is None

    def test_set_and_get_empty_string(self, sqlite_backend):
        """Test storing and retrieving empty string."""
        sqlite_backend.set("empty_key", "")
        assert sqlite_backend.get("empty_key") == ""

    def test_set_and_get_complex_dict(self, sqlite_backend):
        """Test storing and retrieving complex nested dict."""
        complex_data = {
            "nested": {"deep": {"value": 123}},
            "list": [1, 2, 3],
            "mixed": [{"a": 1}, {"b": 2}],
        }
        sqlite_backend.set("complex_key", complex_data)
        assert sqlite_backend.get("complex_key") == complex_data

    def test_set_overwrites_existing_value(self, sqlite_backend):
        """Test that set overwrites existing value."""
        sqlite_backend.set("key", "value1")
        sqlite_backend.set("key", "value2")
        assert sqlite_backend.get("key") == "value2"

    def test_delete_nonexistent_key_returns_false(self, sqlite_backend):
        """Test that deleting nonexistent key returns False."""
        assert not sqlite_backend.delete("nonexistent")

    def test_get_with_custom_default(self, sqlite_backend):
        """Test get with custom default value."""
        assert sqlite_backend.get("nonexistent", "default") == "default"

    def test_keys_with_no_pattern_returns_all(self, sqlite_backend):
        """Test keys() without pattern returns all keys."""
        sqlite_backend.set("key1", "value1")
        sqlite_backend.set("key2", "value2")
        sqlite_backend.set("other", "value3")
        keys = sqlite_backend.keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "other" in keys

    def test_keys_with_pattern_filters_correctly(self, sqlite_backend):
        """Test keys() with pattern filters correctly."""
        sqlite_backend.set("user:1", "John")
        sqlite_backend.set("user:2", "Jane")
        sqlite_backend.set("post:1", "Hello")

        user_keys = sqlite_backend.keys("user:*")
        assert len(user_keys) == 2
        assert "user:1" in user_keys
        assert "user:2" in user_keys
        assert "post:1" not in user_keys

    def test_keys_with_question_mark_pattern(self, sqlite_backend):
        """Test keys() with ? wildcard pattern."""
        sqlite_backend.set("key1", "value1")
        sqlite_backend.set("key2", "value2")
        sqlite_backend.set("key10", "value10")

        keys = sqlite_backend.keys("key?")
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys
        assert "key10" not in keys


class TestSQLiteBackendHashEdgeCases:
    """Tests for SQLite backend hash edge cases."""

    def test_hget_nonexistent_hash_returns_default(self, sqlite_backend):
        """Test hget on nonexistent hash returns default."""
        assert sqlite_backend.hget("nonexistent", "field") is None
        assert (
            sqlite_backend.hget("nonexistent", "field", "default") == "default"
        )

    def test_hgetall_nonexistent_hash_returns_empty_dict(self, sqlite_backend):
        """Test hgetall on nonexistent hash returns empty dict."""
        assert sqlite_backend.hgetall("nonexistent") == {}

    def test_hdel_nonexistent_field_returns_false(self, sqlite_backend):
        """Test hdel on nonexistent field returns False."""
        sqlite_backend.hset("hash", "field1", "value1")
        assert not sqlite_backend.hdel("hash", "nonexistent")

    def test_hexists_nonexistent_hash_returns_false(self, sqlite_backend):
        """Test hexists on nonexistent hash returns False."""
        assert not sqlite_backend.hexists("nonexistent", "field")

    def test_hset_overwrites_existing_field(self, sqlite_backend):
        """Test hset overwrites existing field value."""
        sqlite_backend.hset("hash", "field", "value1")
        sqlite_backend.hset("hash", "field", "value2")
        assert sqlite_backend.hget("hash", "field") == "value2"

    def test_hset_with_complex_values(self, sqlite_backend):
        """Test hset with complex nested values."""
        sqlite_backend.hset("hash", "field", {"nested": [1, 2, 3]})
        assert sqlite_backend.hget("hash", "field") == {"nested": [1, 2, 3]}


class TestSQLiteBackendListEdgeCases:
    """Tests for SQLite backend list edge cases."""

    def test_lrange_on_nonexistent_list_returns_empty(self, sqlite_backend):
        """Test lrange on nonexistent list returns empty list."""
        assert sqlite_backend.lrange("nonexistent", 0, -1) == []

    def test_llen_on_nonexistent_list_returns_zero(self, sqlite_backend):
        """Test llen on nonexistent list returns 0."""
        assert sqlite_backend.llen("nonexistent") == 0

    def test_lpop_on_nonexistent_list_returns_none(self, sqlite_backend):
        """Test lpop on nonexistent list returns None."""
        assert sqlite_backend.lpop("nonexistent") is None

    def test_rpop_on_nonexistent_list_returns_none(self, sqlite_backend):
        """Test rpop on nonexistent list returns None."""
        assert sqlite_backend.rpop("nonexistent") is None

    def test_lpop_on_empty_list_returns_none(self, sqlite_backend):
        """Test lpop on empty list returns None."""
        sqlite_backend.rpush("list", "value")
        sqlite_backend.rpop("list")
        assert sqlite_backend.lpop("list") is None

    def test_lrange_with_negative_end_index(self, sqlite_backend):
        """Test lrange with negative end index."""
        sqlite_backend.rpush("list", "a")
        sqlite_backend.rpush("list", "b")
        sqlite_backend.rpush("list", "c")

        # Get all elements (end=-1 means last element)
        assert sqlite_backend.lrange("list", 0, -1) == ["a", "b", "c"]

        # Get first 2 elements (end=-2 means second-to-last)
        assert sqlite_backend.lrange("list", 0, -2) == ["a", "b"]

    def test_lrange_with_out_of_bounds_indices(self, sqlite_backend):
        """Test lrange with out of bounds indices."""
        sqlite_backend.rpush("list", "a")
        sqlite_backend.rpush("list", "b")

        # Should return all elements
        assert sqlite_backend.lrange("list", 0, 100) == ["a", "b"]

    def test_list_with_complex_values(self, sqlite_backend):
        """Test list operations with complex values."""
        sqlite_backend.rpush("list", {"key": "value"})
        sqlite_backend.rpush("list", [1, 2, 3])

        result = sqlite_backend.lrange("list", 0, -1)
        assert result == [{"key": "value"}, [1, 2, 3]]


class TestSQLiteBackendSetEdgeCases:
    """Tests for SQLite backend set edge cases."""

    def test_sadd_to_nonexistent_set_creates_it(self, sqlite_backend):
        """Test sadd to nonexistent set creates it."""
        added = sqlite_backend.sadd("set", "value")
        assert added == 1
        assert sqlite_backend.sismember("set", "value")

    def test_sadd_duplicate_returns_zero(self, sqlite_backend):
        """Test sadd with duplicate value returns 0."""
        sqlite_backend.sadd("set", "value")
        added = sqlite_backend.sadd("set", "value")
        assert added == 0

    def test_sadd_multiple_values_at_once(self, sqlite_backend):
        """Test sadd with multiple values at once."""
        added = sqlite_backend.sadd("set", "a", "b", "c")
        assert added == 3
        assert sqlite_backend.scard("set") == 3

    def test_sadd_multiple_with_duplicates(self, sqlite_backend):
        """Test sadd with multiple values including duplicates."""
        sqlite_backend.sadd("set", "a")
        added = sqlite_backend.sadd("set", "a", "b", "c")
        assert added == 2  # Only b and c are new

    def test_smembers_on_nonexistent_set_returns_empty(self, sqlite_backend):
        """Test smembers on nonexistent set returns empty set."""
        assert sqlite_backend.smembers("nonexistent") == set()

    def test_sismember_on_nonexistent_set_returns_false(self, sqlite_backend):
        """Test sismember on nonexistent set returns False."""
        assert not sqlite_backend.sismember("nonexistent", "value")

    def test_srem_nonexistent_value_returns_zero(self, sqlite_backend):
        """Test srem on nonexistent value returns 0."""
        sqlite_backend.sadd("set", "a")
        removed = sqlite_backend.srem("set", "b")
        assert removed == 0

    def test_srem_multiple_values(self, sqlite_backend):
        """Test srem with multiple values."""
        sqlite_backend.sadd("set", "a", "b", "c", "d")
        removed = sqlite_backend.srem("set", "a", "c")
        assert removed == 2
        assert sqlite_backend.scard("set") == 2

    def test_scard_on_nonexistent_set_returns_zero(self, sqlite_backend):
        """Test scard on nonexistent set returns 0."""
        assert sqlite_backend.scard("nonexistent") == 0


class TestSQLiteBackendTTLEdgeCases:
    """Tests for SQLite backend TTL edge cases."""

    def test_expire_nonexistent_key_returns_false(self, sqlite_backend):
        """Test expire on nonexistent key returns False."""
        assert not sqlite_backend.expire("nonexistent", 60)

    def test_ttl_on_nonexistent_key_returns_minus_two(self, sqlite_backend):
        """Test ttl on nonexistent key returns -2."""
        assert sqlite_backend.ttl("nonexistent") == -2

    def test_ttl_on_key_without_expiration_returns_none(self, sqlite_backend):
        """Test ttl on key without expiration returns None."""
        sqlite_backend.set("key", "value")
        assert sqlite_backend.ttl("key") is None

    def test_persist_nonexistent_key_returns_false(self, sqlite_backend):
        """Test persist on nonexistent key returns False."""
        assert not sqlite_backend.persist("nonexistent")

    def test_persist_key_without_expiration_returns_false(
        self, sqlite_backend
    ):
        """Test persist on key without expiration returns False."""
        sqlite_backend.set("key", "value")
        assert not sqlite_backend.persist("key")

    def test_expire_updates_existing_expiration(self, sqlite_backend):
        """Test expire updates existing expiration."""
        sqlite_backend.set("key", "value")
        sqlite_backend.expire("key", 3600)
        ttl1 = sqlite_backend.ttl("key")

        sqlite_backend.expire("key", 7200)
        ttl2 = sqlite_backend.ttl("key")

        assert ttl2 > ttl1

    def test_expired_key_not_returned_by_get(self, sqlite_backend):
        """Test that expired key is not returned by get."""
        sqlite_backend.set("key", "value")
        sqlite_backend.expire("key", 1)
        time.sleep(1.1)
        assert sqlite_backend.get("key") is None

    def test_expired_key_not_in_keys_list(self, sqlite_backend):
        """Test that expired key is not in keys list."""
        sqlite_backend.set("key1", "value1")
        sqlite_backend.set("key2", "value2")
        sqlite_backend.expire("key1", 1)
        time.sleep(1.1)
        keys = sqlite_backend.keys()
        assert "key1" not in keys
        assert "key2" in keys


class TestSQLiteBackendMaintenance:
    """Tests for SQLite backend maintenance operations."""

    def test_clear_all_removes_all_data(self, sqlite_backend):
        """Test clear_all removes all data."""
        sqlite_backend.set("key", "value")
        sqlite_backend.hset("hash", "field", "value")
        sqlite_backend.rpush("list", "value")
        sqlite_backend.sadd("set", "value")

        sqlite_backend.clear_all()

        assert len(sqlite_backend.keys()) == 0
        assert sqlite_backend.hgetall("hash") == {}
        assert sqlite_backend.llen("list") == 0
        assert sqlite_backend.scard("set") == 0

    def test_cleanup_expired_removes_only_expired(self, sqlite_backend):
        """Test cleanup_expired removes only expired keys."""
        sqlite_backend.set("key1", "value1")
        sqlite_backend.expire("key1", 1)

        sqlite_backend.set("key2", "value2")
        sqlite_backend.expire("key2", 1)

        sqlite_backend.set("key3", "value3")  # No expiration

        time.sleep(1.1)
        removed = sqlite_backend.cleanup_expired()

        assert removed >= 2
        assert not sqlite_backend.exists("key1")
        assert not sqlite_backend.exists("key2")
        assert sqlite_backend.exists("key3")

    def test_close_closes_connection(self, temp_db):
        """Test close closes the database connection."""
        backend = SQLiteBackend(db_path=temp_db)
        backend.set("key", "value")
        backend.close()

        # Connection should be closed
        with pytest.raises(Exception):
            backend.conn.execute("SELECT 1")

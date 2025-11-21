"""SQLite backend implementation for state management."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

from dotfiles_state_manager.backends.base import StateBackend


class SQLiteBackend(StateBackend):
    """SQLite-based state backend.

    Implements a Redis-like API using SQLite for persistence.
    Uses separate tables for different data structures (key-value, hash, list, set).
    """

    def __init__(self, db_path: Path | str, wal_mode: bool = True) -> None:
        """Initialize SQLite backend.

        Args:
            db_path: Path to SQLite database file
            wal_mode: Enable WAL mode for better concurrency
        """
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()  # Reentrant lock for thread safety

        self.conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            isolation_level=None,  # Autocommit mode
        )

        if wal_mode:
            self.conn.execute("PRAGMA journal_mode=WAL")

        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        # Key-value table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at INTEGER
            )
        """)

        # Hash table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS hash_store (
                hash_key TEXT NOT NULL,
                field TEXT NOT NULL,
                value TEXT NOT NULL,
                expires_at INTEGER,
                PRIMARY KEY (hash_key, field)
            )
        """)

        # List table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS list_store (
                list_key TEXT NOT NULL,
                position INTEGER NOT NULL,
                value TEXT NOT NULL,
                expires_at INTEGER,
                PRIMARY KEY (list_key, position)
            )
        """)

        # Set table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS set_store (
                set_key TEXT NOT NULL,
                value TEXT NOT NULL,
                expires_at INTEGER,
                PRIMARY KEY (set_key, value)
            )
        """)

        # Create indexes for expiration cleanup
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_kv_expires ON kv_store(expires_at)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_hash_expires ON hash_store(expires_at)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_list_expires ON list_store(expires_at)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_set_expires ON set_store(expires_at)"
        )

    def _serialize(self, value: Any) -> str:
        """Serialize a value to JSON string."""
        return json.dumps(value)

    def _deserialize(self, value: str) -> Any:
        """Deserialize a JSON string to value."""
        return json.loads(value)

    def _current_timestamp(self) -> int:
        """Get current Unix timestamp."""
        return int(time.time())

    def _is_expired(self, expires_at: int | None) -> bool:
        """Check if a timestamp indicates expiration."""
        if expires_at is None:
            return False
        return expires_at <= self._current_timestamp()

    # === Key-Value Operations ===

    def set(self, key: str, value: Any) -> None:
        """Store a value for the given key."""
        with self._lock:
            serialized = self._serialize(value)
            self.conn.execute(
                "INSERT OR REPLACE INTO kv_store (key, value, expires_at) VALUES (?, ?, NULL)",
                (key, serialized),
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value for the given key."""
        with self._lock:
            cursor = self.conn.execute(
                "SELECT value, expires_at FROM kv_store WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()

            if row is None:
                return default

            value, expires_at = row

            if self._is_expired(expires_at):
                self.delete(key)
                return default

            return self._deserialize(value)

    def delete(self, key: str) -> bool:
        """Delete a key."""
        cursor = self.conn.execute(
            "DELETE FROM kv_store WHERE key = ?",
            (key,),
        )
        return cursor.rowcount > 0

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        cursor = self.conn.execute(
            "SELECT expires_at FROM kv_store WHERE key = ?",
            (key,),
        )
        row = cursor.fetchone()

        if row is None:
            return False

        expires_at = row[0]
        if self._is_expired(expires_at):
            self.delete(key)
            return False

        return True

    def keys(self, pattern: str | None = None) -> list[str]:
        """List all keys, optionally matching a pattern."""
        cursor = self.conn.execute("SELECT key, expires_at FROM kv_store")
        all_keys = []

        for key, expires_at in cursor.fetchall():
            if not self._is_expired(expires_at):
                if pattern is None or fnmatch(key, pattern):
                    all_keys.append(key)

        return all_keys

    # === Hash Operations ===

    def hset(self, hash_key: str, field: str, value: Any) -> None:
        """Set a field in a hash."""
        serialized = self._serialize(value)
        self.conn.execute(
            """INSERT OR REPLACE INTO hash_store (hash_key, field, value, expires_at)
               VALUES (?, ?, ?, NULL)""",
            (hash_key, field, serialized),
        )

    def hget(self, hash_key: str, field: str, default: Any = None) -> Any:
        """Get a field from a hash."""
        cursor = self.conn.execute(
            "SELECT value, expires_at FROM hash_store WHERE hash_key = ? AND field = ?",
            (hash_key, field),
        )
        row = cursor.fetchone()

        if row is None:
            return default

        value, expires_at = row

        if self._is_expired(expires_at):
            self.hdel(hash_key, field)
            return default

        return self._deserialize(value)

    def hgetall(self, hash_key: str) -> dict[str, Any]:
        """Get all fields from a hash."""
        cursor = self.conn.execute(
            "SELECT field, value, expires_at FROM hash_store WHERE hash_key = ?",
            (hash_key,),
        )

        result = {}
        for field, value, expires_at in cursor.fetchall():
            if not self._is_expired(expires_at):
                result[field] = self._deserialize(value)

        return result

    def hdel(self, hash_key: str, field: str) -> bool:
        """Delete a field from a hash."""
        cursor = self.conn.execute(
            "DELETE FROM hash_store WHERE hash_key = ? AND field = ?",
            (hash_key, field),
        )
        return cursor.rowcount > 0

    def hexists(self, hash_key: str, field: str) -> bool:
        """Check if a field exists in a hash."""
        cursor = self.conn.execute(
            "SELECT expires_at FROM hash_store WHERE hash_key = ? AND field = ?",
            (hash_key, field),
        )
        row = cursor.fetchone()

        if row is None:
            return False

        expires_at = row[0]
        if self._is_expired(expires_at):
            self.hdel(hash_key, field)
            return False

        return True

    # === List Operations ===

    def lpush(self, list_key: str, value: Any) -> None:
        """Prepend a value to a list."""
        # Get all existing items
        cursor = self.conn.execute(
            """SELECT position, value, expires_at FROM list_store
               WHERE list_key = ?
               ORDER BY position""",
            (list_key,),
        )
        existing = cursor.fetchall()

        # Delete all items for this list
        self.conn.execute(
            "DELETE FROM list_store WHERE list_key = ?",
            (list_key,),
        )

        # Insert new item at position 0
        serialized = self._serialize(value)
        self.conn.execute(
            """INSERT INTO list_store (list_key, position, value, expires_at)
               VALUES (?, 0, ?, NULL)""",
            (list_key, serialized),
        )

        # Re-insert existing items with shifted positions
        for pos, val, exp in existing:
            self.conn.execute(
                """INSERT INTO list_store (list_key, position, value, expires_at)
                   VALUES (?, ?, ?, ?)""",
                (list_key, pos + 1, val, exp),
            )

    def rpush(self, list_key: str, value: Any) -> None:
        """Append a value to a list."""
        # Get max position
        cursor = self.conn.execute(
            "SELECT MAX(position) FROM list_store WHERE list_key = ?",
            (list_key,),
        )
        row = cursor.fetchone()
        max_pos = row[0] if row[0] is not None else -1

        # Insert at next position
        serialized = self._serialize(value)
        self.conn.execute(
            """INSERT INTO list_store (list_key, position, value, expires_at)
               VALUES (?, ?, ?, NULL)""",
            (list_key, max_pos + 1, serialized),
        )

    def lrange(
        self, list_key: str, start: int = 0, end: int = -1
    ) -> list[Any]:
        """Get a range of elements from a list."""
        # Get list length
        length = self.llen(list_key)

        if length == 0:
            return []

        # Handle negative indices
        if end < 0:
            end = length + end

        # Clamp to valid range
        start = max(0, start)
        end = min(length - 1, end)

        if start > end:
            return []

        cursor = self.conn.execute(
            """SELECT value FROM list_store
               WHERE list_key = ? AND position >= ? AND position <= ?
               AND (expires_at IS NULL OR expires_at > ?)
               ORDER BY position""",
            (list_key, start, end, self._current_timestamp()),
        )

        return [self._deserialize(row[0]) for row in cursor.fetchall()]

    def llen(self, list_key: str) -> int:
        """Get the length of a list."""
        cursor = self.conn.execute(
            """SELECT COUNT(*) FROM list_store
               WHERE list_key = ? AND (expires_at IS NULL OR expires_at > ?)""",
            (list_key, self._current_timestamp()),
        )
        return cursor.fetchone()[0]

    def lpop(self, list_key: str) -> Any | None:
        """Remove and return the first element of a list."""
        cursor = self.conn.execute(
            """SELECT value FROM list_store
               WHERE list_key = ? AND position = 0
               AND (expires_at IS NULL OR expires_at > ?)""",
            (list_key, self._current_timestamp()),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        value = self._deserialize(row[0])

        # Delete the element
        self.conn.execute(
            "DELETE FROM list_store WHERE list_key = ? AND position = 0",
            (list_key,),
        )

        # Shift all positions down by 1
        self.conn.execute(
            "UPDATE list_store SET position = position - 1 WHERE list_key = ?",
            (list_key,),
        )

        return value

    def rpop(self, list_key: str) -> Any | None:
        """Remove and return the last element of a list."""
        cursor = self.conn.execute(
            """SELECT position, value FROM list_store
               WHERE list_key = ? AND (expires_at IS NULL OR expires_at > ?)
               ORDER BY position DESC LIMIT 1""",
            (list_key, self._current_timestamp()),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        position, value = row
        value = self._deserialize(value)

        # Delete the element
        self.conn.execute(
            "DELETE FROM list_store WHERE list_key = ? AND position = ?",
            (list_key, position),
        )

        return value

    # === Set Operations ===

    def sadd(self, set_key: str, *values: Any) -> int:
        """Add one or more values to a set."""
        added = 0
        for value in values:
            serialized = self._serialize(value)
            try:
                self.conn.execute(
                    """INSERT INTO set_store (set_key, value, expires_at)
                       VALUES (?, ?, NULL)""",
                    (set_key, serialized),
                )
                added += 1
            except sqlite3.IntegrityError:
                # Value already exists in set
                pass
        return added

    def smembers(self, set_key: str) -> set[Any]:
        """Get all members of a set."""
        cursor = self.conn.execute(
            """SELECT value FROM set_store
               WHERE set_key = ? AND (expires_at IS NULL OR expires_at > ?)""",
            (set_key, self._current_timestamp()),
        )
        return {self._deserialize(row[0]) for row in cursor.fetchall()}

    def sismember(self, set_key: str, value: Any) -> bool:
        """Check if a value is a member of a set."""
        serialized = self._serialize(value)
        cursor = self.conn.execute(
            """SELECT expires_at FROM set_store
               WHERE set_key = ? AND value = ?""",
            (set_key, serialized),
        )
        row = cursor.fetchone()

        if row is None:
            return False

        expires_at = row[0]
        if self._is_expired(expires_at):
            self.srem(set_key, value)
            return False

        return True

    def srem(self, set_key: str, *values: Any) -> int:
        """Remove one or more values from a set."""
        removed = 0
        for value in values:
            serialized = self._serialize(value)
            cursor = self.conn.execute(
                "DELETE FROM set_store WHERE set_key = ? AND value = ?",
                (set_key, serialized),
            )
            removed += cursor.rowcount
        return removed

    def scard(self, set_key: str) -> int:
        """Get the number of members in a set."""
        cursor = self.conn.execute(
            """SELECT COUNT(*) FROM set_store
               WHERE set_key = ? AND (expires_at IS NULL OR expires_at > ?)""",
            (set_key, self._current_timestamp()),
        )
        return cursor.fetchone()[0]

    # === TTL/Expiration Operations ===

    def expire(self, key: str, seconds: int) -> bool:
        """Set an expiration time on a key."""
        expires_at = self._current_timestamp() + seconds

        # Try to update in kv_store
        cursor = self.conn.execute(
            "UPDATE kv_store SET expires_at = ? WHERE key = ?",
            (expires_at, key),
        )

        if cursor.rowcount > 0:
            return True

        # Try hash_store (set expiration on all fields)
        cursor = self.conn.execute(
            "UPDATE hash_store SET expires_at = ? WHERE hash_key = ?",
            (expires_at, key),
        )

        if cursor.rowcount > 0:
            return True

        # Try list_store
        cursor = self.conn.execute(
            "UPDATE list_store SET expires_at = ? WHERE list_key = ?",
            (expires_at, key),
        )

        if cursor.rowcount > 0:
            return True

        # Try set_store
        cursor = self.conn.execute(
            "UPDATE set_store SET expires_at = ? WHERE set_key = ?",
            (expires_at, key),
        )

        return cursor.rowcount > 0

    def ttl(self, key: str) -> int | None:
        """Get the remaining time to live for a key."""
        # Check kv_store
        cursor = self.conn.execute(
            "SELECT expires_at FROM kv_store WHERE key = ?",
            (key,),
        )
        row = cursor.fetchone()

        if row is not None:
            expires_at = row[0]
            if expires_at is None:
                return None
            remaining = expires_at - self._current_timestamp()
            return max(0, remaining) if remaining > 0 else -2

        # Check hash_store
        cursor = self.conn.execute(
            "SELECT expires_at FROM hash_store WHERE hash_key = ? LIMIT 1",
            (key,),
        )
        row = cursor.fetchone()

        if row is not None:
            expires_at = row[0]
            if expires_at is None:
                return None
            remaining = expires_at - self._current_timestamp()
            return max(0, remaining) if remaining > 0 else -2

        # Check list_store
        cursor = self.conn.execute(
            "SELECT expires_at FROM list_store WHERE list_key = ? LIMIT 1",
            (key,),
        )
        row = cursor.fetchone()

        if row is not None:
            expires_at = row[0]
            if expires_at is None:
                return None
            remaining = expires_at - self._current_timestamp()
            return max(0, remaining) if remaining > 0 else -2

        # Check set_store
        cursor = self.conn.execute(
            "SELECT expires_at FROM set_store WHERE set_key = ? LIMIT 1",
            (key,),
        )
        row = cursor.fetchone()

        if row is not None:
            expires_at = row[0]
            if expires_at is None:
                return None
            remaining = expires_at - self._current_timestamp()
            return max(0, remaining) if remaining > 0 else -2

        return -2  # Key doesn't exist

    def persist(self, key: str) -> bool:
        """Remove expiration from a key."""
        # Try all tables
        updated = False

        cursor = self.conn.execute(
            "UPDATE kv_store SET expires_at = NULL WHERE key = ? AND expires_at IS NOT NULL",
            (key,),
        )
        updated = updated or cursor.rowcount > 0

        cursor = self.conn.execute(
            "UPDATE hash_store SET expires_at = NULL WHERE hash_key = ? AND expires_at IS NOT NULL",
            (key,),
        )
        updated = updated or cursor.rowcount > 0

        cursor = self.conn.execute(
            "UPDATE list_store SET expires_at = NULL WHERE list_key = ? AND expires_at IS NOT NULL",
            (key,),
        )
        updated = updated or cursor.rowcount > 0

        cursor = self.conn.execute(
            "UPDATE set_store SET expires_at = NULL WHERE set_key = ? AND expires_at IS NOT NULL",
            (key,),
        )
        updated = updated or cursor.rowcount > 0

        return updated

    # === Maintenance Operations ===

    def cleanup_expired(self) -> int:
        """Remove all expired keys."""
        current_time = self._current_timestamp()
        total_removed = 0

        cursor = self.conn.execute(
            "DELETE FROM kv_store WHERE expires_at IS NOT NULL AND expires_at <= ?",
            (current_time,),
        )
        total_removed += cursor.rowcount

        cursor = self.conn.execute(
            "DELETE FROM hash_store WHERE expires_at IS NOT NULL AND expires_at <= ?",
            (current_time,),
        )
        total_removed += cursor.rowcount

        cursor = self.conn.execute(
            "DELETE FROM list_store WHERE expires_at IS NOT NULL AND expires_at <= ?",
            (current_time,),
        )
        total_removed += cursor.rowcount

        cursor = self.conn.execute(
            "DELETE FROM set_store WHERE expires_at IS NOT NULL AND expires_at <= ?",
            (current_time,),
        )
        total_removed += cursor.rowcount

        return total_removed

    def clear_all(self) -> None:
        """Clear all data (dangerous!)."""
        self.conn.execute("DELETE FROM kv_store")
        self.conn.execute("DELETE FROM hash_store")
        self.conn.execute("DELETE FROM list_store")
        self.conn.execute("DELETE FROM set_store")

    def close(self) -> None:
        """Close the backend connection and cleanup resources."""
        self.conn.close()

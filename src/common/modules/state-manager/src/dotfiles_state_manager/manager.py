"""Main StateManager facade."""

from __future__ import annotations

from typing import Any

from dotfiles_state_manager.backends import (
    RedisBackend,
    SQLiteBackend,
    StateBackend,
)
from dotfiles_state_manager.config import (
    StateManagerConfig,
    get_state_manager_config,
)


class StateManager:
    """Main state manager facade.

    Provides a unified interface for state persistence that delegates
    to the configured backend (SQLite or Redis).

    Usage:
        # Use default configuration
        state = StateManager()

        # Use custom configuration
        config = StateManagerConfig(backend="redis")
        state = StateManager(config=config)

        # Use specific backend directly
        state = StateManager(backend=SQLiteBackend(db_path=Path("custom.db")))
    """

    def __init__(
        self,
        config: StateManagerConfig | None = None,
        backend: StateBackend | None = None,
    ) -> None:
        """Initialize state manager.

        Args:
            config: Configuration for state manager. If None, loads from settings files.
            backend: Specific backend instance to use. If provided, config is ignored.
        """
        if backend is not None:
            self._backend = backend
        else:
            if config is None:
                config = get_state_manager_config()

            self._backend = self._create_backend(config)

    def _create_backend(self, config: StateManagerConfig) -> StateBackend:
        """Create backend from configuration.

        Args:
            config: State manager configuration

        Returns:
            Configured backend instance

        Raises:
            ValueError: If backend type is not supported
        """
        if config.backend == "sqlite":
            return SQLiteBackend(
                db_path=config.sqlite.db_path,
                wal_mode=config.sqlite.wal_mode,
            )
        elif config.backend == "redis":
            return RedisBackend(
                host=config.redis.host,
                port=config.redis.port,
                db=config.redis.db,
                password=config.redis.password
                if config.redis.password
                else None,
                key_prefix=config.redis.key_prefix,
                max_connections=config.redis.max_connections,
                socket_timeout=config.redis.socket_timeout,
                socket_connect_timeout=config.redis.socket_connect_timeout,
            )
        else:
            raise ValueError(f"Unsupported backend: {config.backend}")

    # === Key-Value Operations ===

    def set(self, key: str, value: Any) -> None:
        """Store a value for the given key."""
        self._backend.set(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value for the given key."""
        return self._backend.get(key, default)

    def delete(self, key: str) -> bool:
        """Delete a key."""
        return self._backend.delete(key)

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return self._backend.exists(key)

    def keys(self, pattern: str | None = None) -> list[str]:
        """List all keys, optionally matching a pattern."""
        return self._backend.keys(pattern)

    # === Hash Operations ===

    def hset(self, hash_key: str, field: str, value: Any) -> None:
        """Set a field in a hash."""
        self._backend.hset(hash_key, field, value)

    def hget(self, hash_key: str, field: str, default: Any = None) -> Any:
        """Get a field from a hash."""
        return self._backend.hget(hash_key, field, default)

    def hgetall(self, hash_key: str) -> dict[str, Any]:
        """Get all fields from a hash."""
        return self._backend.hgetall(hash_key)

    def hdel(self, hash_key: str, field: str) -> bool:
        """Delete a field from a hash."""
        return self._backend.hdel(hash_key, field)

    def hexists(self, hash_key: str, field: str) -> bool:
        """Check if a field exists in a hash."""
        return self._backend.hexists(hash_key, field)

    # === List Operations ===

    def lpush(self, list_key: str, value: Any) -> None:
        """Prepend a value to a list."""
        self._backend.lpush(list_key, value)

    def rpush(self, list_key: str, value: Any) -> None:
        """Append a value to a list."""
        self._backend.rpush(list_key, value)

    def lrange(
        self, list_key: str, start: int = 0, end: int = -1
    ) -> list[Any]:
        """Get a range of elements from a list."""
        return self._backend.lrange(list_key, start, end)

    def llen(self, list_key: str) -> int:
        """Get the length of a list."""
        return self._backend.llen(list_key)

    def lpop(self, list_key: str) -> Any | None:
        """Remove and return the first element of a list."""
        return self._backend.lpop(list_key)

    def rpop(self, list_key: str) -> Any | None:
        """Remove and return the last element of a list."""
        return self._backend.rpop(list_key)

    # === Set Operations ===

    def sadd(self, set_key: str, *values: Any) -> int:
        """Add one or more values to a set."""
        return self._backend.sadd(set_key, *values)

    def smembers(self, set_key: str) -> set[Any]:  # type: ignore
        """Get all members of a set."""
        return self._backend.smembers(set_key)

    def sismember(self, set_key: str, value: Any) -> bool:
        """Check if a value is a member of a set."""
        return self._backend.sismember(set_key, value)

    def srem(self, set_key: str, *values: Any) -> int:
        """Remove one or more values from a set."""
        return self._backend.srem(set_key, *values)

    def scard(self, set_key: str) -> int:
        """Get the number of members in a set."""
        return self._backend.scard(set_key)

    # === TTL/Expiration Operations ===

    def expire(self, key: str, seconds: int) -> bool:
        """Set an expiration time on a key."""
        return self._backend.expire(key, seconds)

    def ttl(self, key: str) -> int | None:
        """Get the remaining time to live for a key."""
        return self._backend.ttl(key)

    def persist(self, key: str) -> bool:
        """Remove expiration from a key."""
        return self._backend.persist(key)

    # === Maintenance Operations ===

    def cleanup_expired(self) -> int:
        """Remove all expired keys."""
        return self._backend.cleanup_expired()

    def clear_all(self) -> None:
        """Clear all data (dangerous!)."""
        self._backend.clear_all()

    def close(self) -> None:
        """Close the backend connection and cleanup resources."""
        self._backend.close()

    # === Context Manager Support ===

    def __enter__(self) -> StateManager:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.close()

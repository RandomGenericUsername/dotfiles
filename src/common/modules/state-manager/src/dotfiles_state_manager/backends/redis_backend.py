"""Redis backend implementation for state management."""

from __future__ import annotations

import json
from fnmatch import fnmatch
from typing import Any

try:
    import redis
    from redis import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None  # type: ignore

from dotfiles_state_manager.backends.base import StateBackend


class RedisBackend(StateBackend):
    """Redis-based state backend.

    Provides a thin wrapper around redis-py client that matches
    the StateBackend interface.

    Requires redis package to be installed:
        uv add dotfiles-state-manager[redis]
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        key_prefix: str = "dotfiles:",
        max_connections: int = 10,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
    ) -> None:
        """Initialize Redis backend.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            key_prefix: Prefix for all keys
            max_connections: Maximum connections in pool
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Socket connect timeout in seconds

        Raises:
            ImportError: If redis package is not installed
            redis.ConnectionError: If cannot connect to Redis
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis backend requires redis package. "
                "Install with: uv add dotfiles-state-manager[redis]"
            )

        self.key_prefix = key_prefix
        self.client: Redis = redis.Redis(  # type: ignore
            host=host,
            port=port,
            db=db,
            password=password if password else None,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            decode_responses=True,
        )

        # Test connection
        try:
            self.client.ping()
        except redis.ConnectionError as e:
            raise redis.ConnectionError(
                f"Cannot connect to Redis at {host}:{port}"
            ) from e

    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.key_prefix}{key}"

    def _serialize(self, value: Any) -> str:
        """Serialize a value to JSON string."""
        return json.dumps(value)

    def _deserialize(self, value: str) -> Any:
        """Deserialize a JSON string to value."""
        return json.loads(value)

    # === Key-Value Operations ===

    def set(self, key: str, value: Any) -> None:
        """Store a value for the given key."""
        prefixed_key = self._make_key(key)
        serialized = self._serialize(value)
        self.client.set(prefixed_key, serialized)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value for the given key."""
        prefixed_key = self._make_key(key)
        value = self.client.get(prefixed_key)

        if value is None:
            return default

        return self._deserialize(value)

    def delete(self, key: str) -> bool:
        """Delete a key."""
        prefixed_key = self._make_key(key)
        result = self.client.delete(prefixed_key)
        return result > 0

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        prefixed_key = self._make_key(key)
        return bool(self.client.exists(prefixed_key))

    def keys(self, pattern: str | None = None) -> list[str]:
        """List all keys, optionally matching a pattern."""
        if pattern is None:
            search_pattern = f"{self.key_prefix}*"
        else:
            search_pattern = f"{self.key_prefix}{pattern}"

        # Get all matching keys
        raw_keys = self.client.keys(search_pattern)

        # Remove prefix from keys
        prefix_len = len(self.key_prefix)
        keys_list = [k[prefix_len:] for k in raw_keys]

        # If pattern was provided, filter with fnmatch
        if pattern is not None:
            keys_list = [k for k in keys_list if fnmatch(k, pattern)]

        return keys_list

    # === Hash Operations ===

    def hset(self, hash_key: str, field: str, value: Any) -> None:
        """Set a field in a hash."""
        prefixed_key = self._make_key(hash_key)
        serialized = self._serialize(value)
        self.client.hset(prefixed_key, field, serialized)

    def hget(self, hash_key: str, field: str, default: Any = None) -> Any:
        """Get a field from a hash."""
        prefixed_key = self._make_key(hash_key)
        value = self.client.hget(prefixed_key, field)

        if value is None:
            return default

        return self._deserialize(value)

    def hgetall(self, hash_key: str) -> dict[str, Any]:
        """Get all fields from a hash."""
        prefixed_key = self._make_key(hash_key)
        raw_hash = self.client.hgetall(prefixed_key)

        return {
            field: self._deserialize(value)
            for field, value in raw_hash.items()
        }

    def hdel(self, hash_key: str, field: str) -> bool:
        """Delete a field from a hash."""
        prefixed_key = self._make_key(hash_key)
        result = self.client.hdel(prefixed_key, field)
        return result > 0

    def hexists(self, hash_key: str, field: str) -> bool:
        """Check if a field exists in a hash."""
        prefixed_key = self._make_key(hash_key)
        return bool(self.client.hexists(prefixed_key, field))

    # === List Operations ===

    def lpush(self, list_key: str, value: Any) -> None:
        """Prepend a value to a list."""
        prefixed_key = self._make_key(list_key)
        serialized = self._serialize(value)
        self.client.lpush(prefixed_key, serialized)

    def rpush(self, list_key: str, value: Any) -> None:
        """Append a value to a list."""
        prefixed_key = self._make_key(list_key)
        serialized = self._serialize(value)
        self.client.rpush(prefixed_key, serialized)

    def lrange(
        self, list_key: str, start: int = 0, end: int = -1
    ) -> list[Any]:
        """Get a range of elements from a list."""
        prefixed_key = self._make_key(list_key)
        values = self.client.lrange(prefixed_key, start, end)
        return [self._deserialize(v) for v in values]

    def llen(self, list_key: str) -> int:
        """Get the length of a list."""
        prefixed_key = self._make_key(list_key)
        return int(self.client.llen(prefixed_key))

    def lpop(self, list_key: str) -> Any | None:
        """Remove and return the first element of a list."""
        prefixed_key = self._make_key(list_key)
        value = self.client.lpop(prefixed_key)

        if value is None:
            return None

        return self._deserialize(value)

    def rpop(self, list_key: str) -> Any | None:
        """Remove and return the last element of a list."""
        prefixed_key = self._make_key(list_key)
        value = self.client.rpop(prefixed_key)

        if value is None:
            return None

        return self._deserialize(value)

    # === Set Operations ===

    def sadd(self, set_key: str, *values: Any) -> int:
        """Add one or more values to a set."""
        prefixed_key = self._make_key(set_key)
        serialized_values = [self._serialize(v) for v in values]
        result = self.client.sadd(prefixed_key, *serialized_values)
        return int(result)

    def smembers(self, set_key: str) -> set[Any]:  # type: ignore
        """Get all members of a set."""
        prefixed_key = self._make_key(set_key)
        raw_members = self.client.smembers(prefixed_key)
        return {self._deserialize(m) for m in raw_members}

    def sismember(self, set_key: str, value: Any) -> bool:
        """Check if a value is a member of a set."""
        prefixed_key = self._make_key(set_key)
        serialized = self._serialize(value)
        return bool(self.client.sismember(prefixed_key, serialized))

    def srem(self, set_key: str, *values: Any) -> int:
        """Remove one or more values from a set."""
        prefixed_key = self._make_key(set_key)
        serialized_values = [self._serialize(v) for v in values]
        result = self.client.srem(prefixed_key, *serialized_values)
        return int(result)

    def scard(self, set_key: str) -> int:
        """Get the number of members in a set."""
        prefixed_key = self._make_key(set_key)
        return int(self.client.scard(prefixed_key))

    # === TTL/Expiration Operations ===

    def expire(self, key: str, seconds: int) -> bool:
        """Set an expiration time on a key."""
        prefixed_key = self._make_key(key)
        result = self.client.expire(prefixed_key, seconds)
        return bool(result)

    def ttl(self, key: str) -> int | None:
        """Get the remaining time to live for a key."""
        prefixed_key = self._make_key(key)
        result = self.client.ttl(prefixed_key)

        if result == -1:
            # Key exists but has no expiration
            return None
        elif result == -2:
            # Key doesn't exist
            return -2
        else:
            # Return remaining seconds
            return result

    def persist(self, key: str) -> bool:
        """Remove expiration from a key."""
        prefixed_key = self._make_key(key)
        result = self.client.persist(prefixed_key)
        return bool(result)

    # === Maintenance Operations ===

    def cleanup_expired(self) -> int:
        """Remove all expired keys.

        Note: Redis automatically removes expired keys, so this is a no-op.
        Returns 0 as we can't determine how many keys were expired.
        """
        return 0

    def clear_all(self) -> None:
        """Clear all data (dangerous!)."""
        # Only delete keys with our prefix
        pattern = f"{self.key_prefix}*"
        keys_to_delete = self.client.keys(pattern)

        if keys_to_delete:
            self.client.delete(*keys_to_delete)

    def close(self) -> None:
        """Close the backend connection and cleanup resources."""
        self.client.close()

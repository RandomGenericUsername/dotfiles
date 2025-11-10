"""Abstract base class for state backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StateBackend(ABC):
    """Abstract interface for state persistence backends.

    This defines the contract that all backend implementations must follow.
    Provides a Redis-like API for generic state management.
    """

    # === Key-Value Operations ===

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Store a value for the given key.

        Args:
            key: The key to store the value under
            value: Any JSON-serializable value
        """
        pass

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value for the given key.

        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist

        Returns:
            The stored value or default if not found
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a key.

        Args:
            key: The key to delete

        Returns:
            True if key was deleted, False if it didn't exist
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists.

        Args:
            key: The key to check

        Returns:
            True if key exists, False otherwise
        """
        pass

    @abstractmethod
    def keys(self, pattern: str | None = None) -> list[str]:
        """List all keys, optionally matching a pattern.

        Args:
            pattern: Optional glob-style pattern (e.g., "wallpaper:*")

        Returns:
            List of matching keys
        """
        pass

    # === Hash Operations ===

    @abstractmethod
    def hset(self, hash_key: str, field: str, value: Any) -> None:
        """Set a field in a hash.

        Args:
            hash_key: The hash key
            field: The field name within the hash
            value: Any JSON-serializable value
        """
        pass

    @abstractmethod
    def hget(self, hash_key: str, field: str, default: Any = None) -> Any:
        """Get a field from a hash.

        Args:
            hash_key: The hash key
            field: The field name within the hash
            default: Default value if field doesn't exist

        Returns:
            The field value or default if not found
        """
        pass

    @abstractmethod
    def hgetall(self, hash_key: str) -> dict[str, Any]:
        """Get all fields from a hash.

        Args:
            hash_key: The hash key

        Returns:
            Dictionary of all field-value pairs
        """
        pass

    @abstractmethod
    def hdel(self, hash_key: str, field: str) -> bool:
        """Delete a field from a hash.

        Args:
            hash_key: The hash key
            field: The field name to delete

        Returns:
            True if field was deleted, False if it didn't exist
        """
        pass

    @abstractmethod
    def hexists(self, hash_key: str, field: str) -> bool:
        """Check if a field exists in a hash.

        Args:
            hash_key: The hash key
            field: The field name to check

        Returns:
            True if field exists, False otherwise
        """
        pass

    # === List Operations ===

    @abstractmethod
    def lpush(self, list_key: str, value: Any) -> None:
        """Prepend a value to a list.

        Args:
            list_key: The list key
            value: Any JSON-serializable value
        """
        pass

    @abstractmethod
    def rpush(self, list_key: str, value: Any) -> None:
        """Append a value to a list.

        Args:
            list_key: The list key
            value: Any JSON-serializable value
        """
        pass

    @abstractmethod
    def lrange(
        self, list_key: str, start: int = 0, end: int = -1
    ) -> list[Any]:
        """Get a range of elements from a list.

        Args:
            list_key: The list key
            start: Start index (0-based, inclusive)
            end: End index (-1 means end of list, inclusive)

        Returns:
            List of values in the specified range
        """
        pass

    @abstractmethod
    def llen(self, list_key: str) -> int:
        """Get the length of a list.

        Args:
            list_key: The list key

        Returns:
            Number of elements in the list
        """
        pass

    @abstractmethod
    def lpop(self, list_key: str) -> Any | None:
        """Remove and return the first element of a list.

        Args:
            list_key: The list key

        Returns:
            The first element or None if list is empty
        """
        pass

    @abstractmethod
    def rpop(self, list_key: str) -> Any | None:
        """Remove and return the last element of a list.

        Args:
            list_key: The list key

        Returns:
            The last element or None if list is empty
        """
        pass

    # === Set Operations ===

    @abstractmethod
    def sadd(self, set_key: str, *values: Any) -> int:
        """Add one or more values to a set.

        Args:
            set_key: The set key
            values: One or more JSON-serializable values

        Returns:
            Number of values actually added (excludes duplicates)
        """
        pass

    @abstractmethod
    def smembers(self, set_key: str) -> set[Any]:
        """Get all members of a set.

        Args:
            set_key: The set key

        Returns:
            Set of all members
        """
        pass

    @abstractmethod
    def sismember(self, set_key: str, value: Any) -> bool:
        """Check if a value is a member of a set.

        Args:
            set_key: The set key
            value: The value to check

        Returns:
            True if value is in set, False otherwise
        """
        pass

    @abstractmethod
    def srem(self, set_key: str, *values: Any) -> int:
        """Remove one or more values from a set.

        Args:
            set_key: The set key
            values: One or more values to remove

        Returns:
            Number of values actually removed
        """
        pass

    @abstractmethod
    def scard(self, set_key: str) -> int:
        """Get the number of members in a set.

        Args:
            set_key: The set key

        Returns:
            Number of members in the set
        """
        pass

    # === TTL/Expiration Operations ===

    @abstractmethod
    def expire(self, key: str, seconds: int) -> bool:
        """Set an expiration time on a key.

        Args:
            key: The key to set expiration on
            seconds: Number of seconds until expiration

        Returns:
            True if expiration was set, False if key doesn't exist
        """
        pass

    @abstractmethod
    def ttl(self, key: str) -> int | None:
        """Get the remaining time to live for a key.

        Args:
            key: The key to check

        Returns:
            Seconds until expiration, None if no expiration set,
            or -2 if key doesn't exist
        """
        pass

    @abstractmethod
    def persist(self, key: str) -> bool:
        """Remove expiration from a key.

        Args:
            key: The key to persist

        Returns:
            True if expiration was removed, False if key doesn't exist
            or has no expiration
        """
        pass

    # === Maintenance Operations ===

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove all expired keys.

        Returns:
            Number of keys removed
        """
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Clear all data (dangerous!).

        Warning: This removes all state. Use with caution.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the backend connection and cleanup resources."""
        pass

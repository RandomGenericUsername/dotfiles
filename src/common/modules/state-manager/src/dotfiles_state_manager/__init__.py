"""Dotfiles State Manager - Generic state persistence layer.

Provides a Redis-like API backed by SQLite or Redis for persistent state management.

Usage:
    from dotfiles_state_manager import StateManager
    
    # Use default configuration (SQLite)
    state = StateManager()
    
    # Key-value operations
    state.set("my_key", "my_value")
    value = state.get("my_key")
    
    # Hash operations
    state.hset("user:1", "name", "John")
    state.hset("user:1", "email", "john@example.com")
    user = state.hgetall("user:1")
    
    # List operations
    state.rpush("tasks", "task1")
    state.rpush("tasks", "task2")
    tasks = state.lrange("tasks", 0, -1)
    
    # Set operations
    state.sadd("tags", "python", "redis", "sqlite")
    tags = state.smembers("tags")
    
    # TTL/Expiration
    state.set("temp_key", "temp_value")
    state.expire("temp_key", 3600)  # Expire in 1 hour
    
    # Context manager
    with StateManager() as state:
        state.set("key", "value")
"""

# Main interface
from dotfiles_state_manager.manager import StateManager

# Backends (for advanced usage)
from dotfiles_state_manager.backends import (
    RedisBackend,
    SQLiteBackend,
    StateBackend,
)

# Configuration
from dotfiles_state_manager.config import (
    AppConfig,
    RedisConfig,
    SQLiteConfig,
    StateManagerConfig,
    get_default_config,
    get_state_manager_config,
)

__all__ = [
    # Main interface
    "StateManager",
    # Backends
    "StateBackend",
    "SQLiteBackend",
    "RedisBackend",
    # Configuration
    "AppConfig",
    "StateManagerConfig",
    "SQLiteConfig",
    "RedisConfig",
    "get_default_config",
    "get_state_manager_config",
]

__version__ = "0.1.0"


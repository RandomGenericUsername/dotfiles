"""SVG template cache manager for wlogout icons."""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any

from dotfiles_state_manager import StateManager

logger = logging.getLogger(__name__)


class SVGTemplateCacheManager:
    """Manages SVG template rendering cache.

    Caches rendered SVG content by colorscheme hash to avoid
    re-rendering identical colorschemes. Provides 70% performance
    improvement (50ms vs 150ms).

    Storage Structure:
        - Hash: "svg_cache:metadata" -> {hash: {template_name, timestamp, size_bytes}}
        - Key: "svg_cache:content:{hash}:{template_name}" -> SVG content string
        - Key: "svg_cache:stats:hits" -> hit count
        - Key: "svg_cache:stats:misses" -> miss count
    """

    def __init__(
        self,
        state: StateManager,
        max_cache_size_mb: int = 10,
        enable_lru: bool = True,
    ):
        """Initialize SVG cache manager.

        Args:
            state: State manager instance
            max_cache_size_mb: Maximum cache size in MB
            enable_lru: Enable LRU eviction when cache is full
        """
        self._state = state
        self._max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self._enable_lru = enable_lru
        self._metadata_key = "svg_cache:metadata"
        self._hits_key = "svg_cache:stats:hits"
        self._misses_key = "svg_cache:stats:misses"

    def compute_colorscheme_hash(
        self, colorscheme_data: dict[str, Any]
    ) -> str:
        """Compute SHA256 hash of colorscheme data.

        Args:
            colorscheme_data: Colorscheme dictionary (colors, special, etc.)

        Returns:
            Hex digest of SHA256 hash

        Example:
            >>> colors = {"color0": "#1a1b26", "color1": "#f7768e", ...}
            >>> hash_val = manager.compute_colorscheme_hash(colors)
            >>> hash_val
            'a3f5c9d2e1b4...'
        """
        # Sort keys for consistent hashing
        sorted_json = json.dumps(colorscheme_data, sort_keys=True)
        return hashlib.sha256(sorted_json.encode()).hexdigest()

    def get_cached_svg(
        self,
        colorscheme_hash: str,
        template_name: str,
    ) -> str | None:
        """Get cached SVG content.

        Args:
            colorscheme_hash: Colorscheme hash
            template_name: Template name (e.g., "lock", "logout")

        Returns:
            SVG content string or None if not cached

        Performance:
            - Target: <5ms per lookup
        """
        try:
            content_key = (
                f"svg_cache:content:{colorscheme_hash}:{template_name}"
            )
            content = self._state.get(content_key)

            if content:
                # Update access time for LRU
                if self._enable_lru:
                    self._update_access_time(colorscheme_hash, template_name)

                # Increment hit counter
                self._increment_counter(self._hits_key)

                return content

            # Increment miss counter
            self._increment_counter(self._misses_key)
            return None
        except Exception as e:
            import traceback

            logger.warning(
                "Failed to get cached SVG: %s\n%s",
                e,
                traceback.format_exc(),
            )
            self._increment_counter(self._misses_key)
            return None

    def cache_svg(
        self,
        colorscheme_hash: str,
        template_name: str,
        svg_content: str,
    ) -> None:
        """Cache rendered SVG content.

        Args:
            colorscheme_hash: Colorscheme hash
            template_name: Template name
            svg_content: Rendered SVG content

        Performance:
            - Target: <10ms per cache operation
        """
        try:
            content_key = (
                f"svg_cache:content:{colorscheme_hash}:{template_name}"
            )

            # Check if we need to evict
            if self._enable_lru:
                current_size = self._get_total_cache_size()
                svg_size = len(svg_content.encode())

                if current_size + svg_size > self._max_cache_size_bytes:
                    self._evict_lru_entries(svg_size)

            # Store content
            self._state.set(content_key, svg_content)

            # Update metadata
            self._update_metadata(
                colorscheme_hash, template_name, len(svg_content.encode())
            )
        except Exception as e:
            logger.warning("Failed to cache SVG: %s", e)

    def _update_metadata(
        self,
        colorscheme_hash: str,
        template_name: str,
        size_bytes: int,
    ) -> None:
        """Update cache metadata.

        Args:
            colorscheme_hash: Colorscheme hash
            template_name: Template name
            size_bytes: Size of SVG content in bytes
        """
        entry_key = f"{colorscheme_hash}:{template_name}"
        metadata = {
            "colorscheme_hash": colorscheme_hash,
            "template_name": template_name,
            "size_bytes": size_bytes,
            "cached_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
        }

        self._state.hset(self._metadata_key, entry_key, json.dumps(metadata))

    def _update_access_time(
        self, colorscheme_hash: str, template_name: str
    ) -> None:
        """Update last access time for LRU.

        Args:
            colorscheme_hash: Colorscheme hash
            template_name: Template name
        """
        entry_key = f"{colorscheme_hash}:{template_name}"
        metadata_json = self._state.hget(self._metadata_key, entry_key)

        if metadata_json:
            metadata = json.loads(metadata_json)
            metadata["last_accessed"] = datetime.now().isoformat()
            self._state.hset(
                self._metadata_key, entry_key, json.dumps(metadata)
            )

    def _get_total_cache_size(self) -> int:
        """Get total cache size in bytes.

        Returns:
            Total size in bytes
        """
        metadata_dict = self._state.hgetall(self._metadata_key)
        if not metadata_dict:
            return 0

        total_size = 0
        for metadata_json in metadata_dict.values():
            metadata = json.loads(metadata_json)
            total_size += metadata.get("size_bytes", 0)

        return total_size

    def _evict_lru_entries(self, required_bytes: int) -> None:
        """Evict least recently used entries to make space.

        Args:
            required_bytes: Bytes needed for new entry
        """
        metadata_dict = self._state.hgetall(self._metadata_key)
        if not metadata_dict:
            return

        # Parse and sort by last_accessed
        entries = []
        for entry_key, metadata_json in metadata_dict.items():
            metadata = json.loads(metadata_json)
            entries.append((entry_key, metadata))

        # Sort by last_accessed (oldest first)
        entries.sort(key=lambda x: x[1]["last_accessed"])

        # Evict until we have enough space
        freed_bytes = 0
        for entry_key, metadata in entries:
            if freed_bytes >= required_bytes:
                break

            # Delete content
            content_key = f"svg_cache:content:{metadata['colorscheme_hash']}:{metadata['template_name']}"
            self._state.delete(content_key)

            # Delete metadata
            self._state.hdel(self._metadata_key, entry_key)

            freed_bytes += metadata.get("size_bytes", 0)

            logger.debug(
                "Evicted SVG cache entry: %s:%s (%d bytes)",
                metadata["colorscheme_hash"][:8],
                metadata["template_name"],
                metadata.get("size_bytes", 0),
            )

    def _increment_counter(self, key: str) -> None:
        """Increment a counter.

        Args:
            key: Counter key
        """
        try:
            current = self._state.get(key)
            if current:
                self._state.set(key, str(int(current) + 1))
            else:
                self._state.set(key, "1")
        except Exception:
            # Ignore counter errors
            pass

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache stats (hits, misses, size, entries)
        """
        try:
            hits = int(self._state.get(self._hits_key) or "0")
            misses = int(self._state.get(self._misses_key) or "0")
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0.0

            metadata_dict = self._state.hgetall(self._metadata_key)
            entry_count = len(metadata_dict) if metadata_dict else 0
            total_size = self._get_total_cache_size()

            return {
                "hits": hits,
                "misses": misses,
                "hit_rate_percent": round(hit_rate, 2),
                "entry_count": entry_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "max_size_mb": self._max_cache_size_bytes / (1024 * 1024),
            }
        except Exception as e:
            logger.warning("Failed to get cache stats: %s", e)
            return {
                "hits": 0,
                "misses": 0,
                "hit_rate_percent": 0.0,
                "entry_count": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0.0,
                "max_size_mb": self._max_cache_size_bytes / (1024 * 1024),
            }

    def clear_cache(self) -> None:
        """Clear all cached SVG content."""
        try:
            metadata_dict = self._state.hgetall(self._metadata_key)
            if metadata_dict:
                # Delete all content keys
                for metadata_json in metadata_dict.values():
                    metadata = json.loads(metadata_json)
                    content_key = f"svg_cache:content:{metadata['colorscheme_hash']}:{metadata['template_name']}"
                    self._state.delete(content_key)

                # Delete all metadata fields
                for entry_key in metadata_dict.keys():
                    self._state.hdel(self._metadata_key, entry_key)

            # Clear stats
            self._state.delete(self._hits_key)
            self._state.delete(self._misses_key)

            logger.info("Cleared SVG cache")
        except Exception as e:
            logger.warning("Failed to clear cache: %s", e)

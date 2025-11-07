"""
Explicit path builder for defining directory structures with hidden status.

This module provides a builder pattern for explicitly defining all paths
in your project with their hidden status, replacing dynamic attribute access
with explicit configuration.

Usage:
    builder = PathsBuilder(Path.home() / "dotfiles")
    builder.add_path("dotfiles", hidden=True)
    builder.add_path("dotfiles.starship", hidden=True)
    builder.add_path("config", hidden=True)
    builder.add_path("scripts", hidden=False)

    # Build returns a ManagedPathTree with create() and navigation
    paths = builder.build()
    paths.create()              # Creates all registered directories
    paths.dotfiles.path         # Navigate to dotfiles path
    paths.scripts.ensure_dir()  # Create individual directory
"""

from dataclasses import dataclass, field
from pathlib import Path

from filesystem_path_builder.pathtree import PathTree


def _sanitize_key(key: str) -> str:
    """Sanitize a path key for Python attribute access.

    Converts the key to a Python-friendly format:
    - Lowercase
    - Spaces → underscores
    - Hyphens → underscores
    - Dots preserved (for nesting)

    Args:
        key: Original path key (e.g., "dotfiles.My Config-Files")

    Returns:
        Sanitized key (e.g., "dotfiles.my_config_files")

    Example:
        >>> _sanitize_key("dotfiles.Oh-My-Zsh")
        'dotfiles.oh_my_zsh'
        >>> _sanitize_key("Wallpapers Directory")
        'wallpapers_directory'
    """
    # Split by dots to preserve nesting
    parts = key.split(".")
    # Sanitize each component: lowercase, spaces/hyphens → underscores
    sanitized_parts = [
        part.lower().replace(" ", "_").replace("-", "_") for part in parts
    ]
    # Rejoin with dots
    return ".".join(sanitized_parts)


@dataclass
class PathDefinition:
    """Definition of a single path with its properties.

    The key is normalized (lowercase, spaces/hyphens → underscores) for Python
    attribute access, while original_key preserves the original component
    names for directory creation.

    This allows defining paths like "dotfiles.Oh-My Zsh" (with mixed case,
    spaces, hyphens) while accessing them via attributes like
    dotfiles.oh_my_zsh (with underscores).
    """

    key: str  # Normalized key for registry lookups (lowercase, underscores)
    original_key: (
        str  # Original key as provided (preserves case, spaces, hyphens)
    )
    hidden: bool = False

    def get_parts(self) -> list[str]:
        """Get path components from original key.

        Preserves case, spaces, hyphens.
        """
        return self.original_key.split(".")


class PathsBuilder:
    """Builder for explicitly defining directory structures.

    This class allows you to define all paths in your project explicitly,
    specifying which ones should be hidden. It builds a namespace object
    that provides attribute access to all defined paths.

    The builder supports strict mode, which enforces that only registered
    paths can be accessed. This helps catch typos and ensures all paths
    are explicitly defined.

    Example:
        >>> # Flexible mode (default) - allows dynamic navigation
        >>> builder = PathsBuilder(Path.home() / "dotfiles")
        >>> builder.add_path("dotfiles", hidden=True)
        >>> builder.add_path("dotfiles.starship", hidden=True)
        >>> paths = builder.build()
        >>> paths.dotfiles.path  # Registered path
        PosixPath('/home/user/.dotfiles')
        >>> paths.scripts.path  # Dynamic navigation allowed
        PosixPath('/home/user/dotfiles/scripts')

        >>> # Strict mode - only registered paths allowed
        >>> builder = PathsBuilder(Path.home() / "dotfiles", strict=True)
        >>> builder.add_path("dotfiles", hidden=True)
        >>> paths = builder.build()
        >>> paths.dotfiles.path  # OK - registered
        PosixPath('/home/user/.dotfiles')
        >>> paths.scripts.path  # Error - not registered
        AttributeError: Path 'scripts' is not registered...
    """

    def __init__(self, root: Path, strict: bool = False):
        """Initialize builder with root directory.

        Args:
            root: Root directory for all paths
            strict: If True, only registered paths can be accessed.
                   If False (default), allows dynamic navigation.
        """
        self.root = Path(root)
        self.strict = strict
        self.definitions: dict[str, PathDefinition] = {}

    def add_path(self, key: str, hidden: bool = False) -> "PathsBuilder":
        """Add a path definition.

        The key is stored exactly as provided. For attribute access, use
        Python-friendly names (lowercase, underscores). For paths with
        hyphens, spaces, or mixed case, use bracket notation.

        Args:
            key: Dot-separated path key (e.g., "dotfiles.config")
            hidden: Whether this directory should be hidden (prefixed with .)

        Returns:
            Self for method chaining

        Example:
            >>> builder = PathsBuilder(Path.home() / "dotfiles")
            >>> builder.add_path("dotfiles", hidden=True)
            >>> builder.add_path("dotfiles.oh_my_zsh", hidden=True)
            >>> builder.add_path("dotfiles.oh-my-zsh")  # Different path!
            >>> paths = builder.build()
            >>> # Attribute access (Python-friendly names)
            >>> paths.dotfiles.oh_my_zsh.path
            PosixPath('/home/user/.dotfiles/.oh_my_zsh')
            >>> # Bracket access (any name)
            >>> paths.dotfiles["oh-my-zsh"].path
            PosixPath('/home/user/.dotfiles/oh-my-zsh')
        """
        # Store with original key (no sanitization)
        self.definitions[key] = PathDefinition(
            key=key, original_key=key, hidden=hidden
        )
        return self

    def build(self) -> "ManagedPathTree":
        """Build a ManagedPathTree with all definitions.

        Creates a ManagedPathTree instance that combines navigation,
        path methods, and bulk directory creation.

        Returns:
            ManagedPathTree instance with full registry

        Example:
            >>> builder = PathsBuilder(Path.home() / "dotfiles")
            >>> builder.add_path("dotfiles", hidden=True)
            >>> builder.add_path("scripts", hidden=False)
            >>> paths = builder.build()
            >>> paths.create()  # Create all directories
            >>> paths.dotfiles.path
            PosixPath('/home/user/.dotfiles')
        """
        return ManagedPathTree(
            base=self.root,
            rel=Path(),
            hidden=False,
            _registry=self.definitions.copy(),
            _strict=self.strict,
        )

    def create(self) -> list[Path]:
        """Create all defined directories on the filesystem.

        Creates all directories that were added via add_path(), respecting
        the hidden flag for each directory and its parent directories.

        Returns:
            List of Path objects for all created directories

        Example:
            >>> builder = PathsBuilder(Path.home() / ".config")
            >>> builder.add_path("nvim", hidden=False)
            >>> builder.add_path("nvim.lua", hidden=False)
            >>> builder.add_path("nvim.lua.plugins", hidden=False)
            >>> builder.add_path("starship", hidden=False)
            >>> created = builder.create()
            >>> # All directories are now created on disk
        """
        created_paths = []

        for _key, definition in self.definitions.items():
            parts = definition.get_parts()

            # Build path component by component, checking hidden status
            path_components = []
            for i in range(len(parts)):
                # Build key for this level (from original parts)
                level_key = ".".join(parts[: i + 1])
                component = parts[i]

                # Check if this level is marked as hidden
                if (
                    level_key in self.definitions
                    and self.definitions[level_key].hidden
                ):
                    component = f".{component}"

                path_components.append(component)

            # Build final path with all components
            final_path = self.root / Path(*path_components)
            final_path.mkdir(parents=True, exist_ok=True)
            created_paths.append(final_path)

        return created_paths


@dataclass(frozen=True)
class ManagedPathTree(PathTree):
    """PathTree with registry and create() capability.

    Combines PathTree's navigation and path methods with PathsBuilder's
    bulk directory creation capability. This is the recommended way to
    manage directory structures.

    Supports strict mode to enforce that only registered paths can be accessed,
    helping catch typos and ensuring all paths are explicitly defined.

    Attributes:
        base: The root directory for this PathTree
        rel: The relative path from base to current position
        hidden: Whether this directory should be hidden (prefixed with .)
        _registry: Internal registry of all path definitions
        _strict: If True, only registered paths can be accessed

    Example:
        >>> # Flexible mode (default)
        >>> builder = PathsBuilder(Path.home() / "dotfiles")
        >>> builder.add_path("dotfiles", hidden=True)
        >>> builder.add_path("dotfiles.starship", hidden=True)
        >>> paths = builder.build()
        >>> paths.dotfiles.starship.path  # Registered
        PosixPath('/home/user/.dotfiles/.starship')
        >>> paths.scripts.path  # Dynamic navigation allowed
        PosixPath('/home/user/dotfiles/scripts')

        >>> # Strict mode
        >>> builder = PathsBuilder(Path.home() / "dotfiles", strict=True)
        >>> builder.add_path("dotfiles", hidden=True)
        >>> paths = builder.build()
        >>> paths.dotfiles.path  # OK - registered
        PosixPath('/home/user/.dotfiles')
        >>> paths.scripts.path  # Error - not registered
        AttributeError: Path 'scripts' is not registered...
    """

    _registry: dict[str, PathDefinition] = field(
        default_factory=dict, repr=False, compare=False
    )
    _strict: bool = field(default=False, repr=False, compare=False)

    def create(self) -> list[Path]:
        """Create all registered directories on the filesystem.

        Creates all directories that were registered via
        PathsBuilder.add_path(), respecting the hidden flag for each
        directory and its parent directories.

        Returns:
            List of Path objects for all created directories

        Example:
            >>> builder = PathsBuilder(Path.home() / ".config")
            >>> builder.add_path("nvim", hidden=False)
            >>> builder.add_path("nvim.lua", hidden=False)
            >>> builder.add_path("starship", hidden=False)
            >>> paths = builder.build()
            >>> created = paths.create()
            >>> # All directories are now created on disk
        """
        created_paths = []

        for _key, definition in self._registry.items():
            parts = definition.get_parts()

            # Build path component by component, checking hidden status
            # for each level
            path_components = []
            for i in range(len(parts)):
                # Build key for this level (from original parts)
                level_key = ".".join(parts[: i + 1])
                component = parts[i]

                # Check if this level is marked as hidden in registry
                if (
                    level_key in self._registry
                    and self._registry[level_key].hidden
                ):
                    component = f".{component}"

                path_components.append(component)

            # Build final path with all components (including hidden parents)
            final_path = self.base / Path(*path_components)
            final_path.mkdir(parents=True, exist_ok=True)
            created_paths.append(final_path)

        return created_paths

    def __fspath__(self) -> str:
        """Support os.PathLike protocol.

        Allows ManagedPathTree to be used directly in os functions
        that accept path-like objects.

        Returns:
            String representation of the path

        Example:
            >>> paths = builder.build()
            >>> import os
            >>> os.path.exists(paths.dotfiles)  # Works!
            True
        """
        return str(self.path)

    def _get_hidden_status(self, rel_path: Path) -> bool:
        """Look up the hidden status for a relative path from the registry.

        Args:
            rel_path: Relative path to look up

        Returns:
            True if the path should be hidden, False otherwise
        """
        # Convert path to dot-separated key
        key = ".".join(rel_path.parts)

        # Look up in registry
        if key in self._registry:
            return self._registry[key].hidden

        # Not in registry, return False (not hidden)
        return False

    @property
    def path(self) -> Path:
        """Get the full path with hidden status applied to all components.

        Unlike PathTree.path which only applies hidden to the last component,
        this checks the registry for each component in the path and applies
        the dot prefix to any that are marked as hidden.

        Uses original component names from the registry, preserving hyphens
        even when accessed via attributes with underscores.

        Returns:
            Complete path with dot prefixes applied to all hidden components

        Example:
            >>> builder = PathsBuilder(Path("/tmp"))
            >>> builder.add_path("dependencies", hidden=True)
            >>> builder.add_path("dependencies.oh-my-zsh", hidden=True)
            >>> paths = builder.build()
            >>> # Access with underscores, creates with hyphens
            >>> paths.dependencies.oh_my_zsh.path
            PosixPath('/tmp/.dependencies/.oh-my-zsh')
        """
        if self.rel == Path():
            return self.base

        # Build path component by component, checking hidden status
        parts = self.rel.parts
        path_components = []

        for i in range(len(parts)):
            # Build key for this level (normalized with underscores)
            level_key = ".".join(parts[: i + 1])

            # Look up in registry to get original component name
            if level_key in self._registry:
                definition = self._registry[level_key]
                # Use original component name (preserves hyphens)
                original_parts = definition.get_parts()
                component = original_parts[-1]

                # Apply hidden prefix if needed
                if definition.hidden:
                    component = f".{component}"
            else:
                # Fallback to attribute name if not in registry
                component = parts[i]

            path_components.append(component)

        # Build final path with all components
        return self.base / Path(*path_components)

    def __getattr__(self, name: str) -> "ManagedPathTree":
        """Navigate to subdirectory via attribute access.

        Overrides PathTree's __getattr__ to return ManagedPathTree
        instead of PathTree, preserving the registry.

        In strict mode, raises AttributeError if the path is not registered.

        Args:
            name: Directory name (trailing underscore removed for keywords)

        Returns:
            New ManagedPathTree instance pointing to the subdirectory

        Raises:
            AttributeError: If strict mode is enabled and path is not
                registered

        Example:
            >>> paths = builder.build()
            >>> paths.dotfiles.starship
            ManagedPathTree(base=/home/user/dotfiles, rel=dotfiles/starship)
        """
        from filesystem_path_builder.pathtree import _clean_segment

        seg = _clean_segment(name)
        new_rel = self.rel / seg

        # In strict mode, check if path is registered
        if self._strict:
            # Convert path to dot-separated key
            key = ".".join(new_rel.parts)
            if key not in self._registry:
                # Build helpful error message
                available = sorted(self._registry.keys())
                raise AttributeError(
                    f"Path '{key}' is not registered in strict mode. "
                    f"Available registered paths: {available}. "
                    f"Register it in directories.py with: "
                    f"builder.add_path('{key}')"
                )

        return ManagedPathTree(
            base=self.base,
            rel=new_rel,
            hidden=self._get_hidden_status(new_rel),
            _registry=self._registry,
            _strict=self._strict,
        )

    def __getitem__(self, key: str | Path) -> "ManagedPathTree":
        """Navigate to subdirectory via bracket notation.

        Overrides PathTree's __getitem__ to return ManagedPathTree
        instead of PathTree, preserving the registry.

        In strict mode, raises KeyError if the path is not registered.

        Args:
            key: Directory name as string or Path

        Returns:
            New ManagedPathTree instance pointing to the subdirectory

        Raises:
            KeyError: If strict mode is enabled and path is not registered

        Example:
            >>> paths = builder.build()
            >>> paths["dotfiles"]["starship"]
            ManagedPathTree(base=/home/user/dotfiles, rel=dotfiles/starship)
        """
        new_rel = self.rel / str(key)

        # In strict mode, check if path is registered
        if self._strict:
            path_key = ".".join(new_rel.parts)
            if path_key not in self._registry:
                available = sorted(self._registry.keys())
                raise KeyError(
                    f"Path '{path_key}' is not registered in strict mode. "
                    f"Available registered paths: {available}. "
                    f"Register it in directories.py with: "
                    f"builder.add_path('{path_key}')"
                )

        return ManagedPathTree(
            base=self.base,
            rel=new_rel,
            hidden=self._get_hidden_status(new_rel),
            _registry=self._registry,
            _strict=self._strict,
        )

    def __truediv__(self, other: str | Path) -> "ManagedPathTree":
        """Navigate to subdirectory via / operator.

        Overrides PathTree's __truediv__ to return ManagedPathTree
        instead of PathTree, preserving the registry.

        In strict mode, raises ValueError if the path is not registered.

        Args:
            other: Directory name as string or Path

        Returns:
            New ManagedPathTree instance pointing to the subdirectory

        Raises:
            ValueError: If strict mode is enabled and path is not registered

        Example:
            >>> paths = builder.build()
            >>> paths / "dotfiles" / "starship"
            ManagedPathTree(base=/home/user/dotfiles, rel=dotfiles/starship)
        """
        new_rel = self.rel / str(other)

        # In strict mode, check if path is registered
        if self._strict:
            path_key = ".".join(new_rel.parts)
            if path_key not in self._registry:
                available = sorted(self._registry.keys())
                raise ValueError(
                    f"Path '{path_key}' is not registered in strict mode. "
                    f"Available registered paths: {available}. "
                    f"Register it in directories.py with: "
                    f"builder.add_path('{path_key}')"
                )

        return ManagedPathTree(
            base=self.base,
            rel=new_rel,
            hidden=self._get_hidden_status(new_rel),
            _registry=self._registry,
            _strict=self._strict,
        )

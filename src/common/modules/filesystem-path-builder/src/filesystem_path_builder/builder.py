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


@dataclass
class PathDefinition:
    """Definition of a single path with its properties.

    The key is normalized (hyphens replaced with underscores) for Python
    attribute access, while original_key preserves the original component
    names for directory creation.

    This allows defining paths like "dotfiles.oh-my-zsh" (with hyphens)
    while accessing them via attributes like dotfiles.oh_my_zsh
    (with underscores).
    """

    key: str  # Normalized key for registry lookups (underscores)
    original_key: str  # Original key as provided (may have hyphens)
    hidden: bool = False

    def get_parts(self) -> list[str]:
        """Get path components from original key (preserves hyphens)."""
        return self.original_key.split(".")


class PathsBuilder:
    """Builder for explicitly defining directory structures.

    This class allows you to define all paths in your project explicitly,
    specifying which ones should be hidden. It builds a namespace object
    that provides attribute access to all defined paths.

    Example:
        >>> builder = PathsBuilder(Path.home() / "dotfiles")
        >>> builder.add_path("dotfiles", hidden=True)
        >>> builder.add_path("dotfiles.starship", hidden=True)
        >>> builder.add_path("scripts", hidden=False)
        >>> paths = builder.build()
        >>> paths.dotfiles.path
        PosixPath('/home/user/.dotfiles')
        >>> paths.scripts.path
        PosixPath('/home/user/dotfiles/scripts')
    """

    def __init__(self, root: Path):
        """Initialize builder with root directory.

        Args:
            root: Root directory for all paths
        """
        self.root = Path(root)
        self.definitions: dict[str, PathDefinition] = {}

    def add_path(self, key: str, hidden: bool = False) -> "PathsBuilder":
        """Add a path definition.

        The key is normalized (hyphens replaced with underscores) for Python
        attribute access, but the original component names are preserved for
        directory creation. This allows using hyphens in path names while
        accessing them via Python attributes with underscores.

        Args:
            key: Dot-separated path key (e.g., "dotfiles.oh-my-zsh")
            hidden: Whether this directory should be hidden (prefixed with .)

        Returns:
            Self for method chaining

        Example:
            >>> builder = PathsBuilder(Path.home() / "dotfiles")
            >>> builder.add_path("dotfiles", hidden=True)
            >>> builder.add_path("dotfiles.oh-my-zsh", hidden=True)
            >>> paths = builder.build()
            >>> # Access with underscores, creates with hyphens
            >>> paths.dotfiles.oh_my_zsh.path
            PosixPath('/home/user/.dotfiles/.oh-my-zsh')
        """
        # Normalize key for registry lookups (hyphens → underscores)
        normalized_key = key.replace("-", "_")
        self.definitions[normalized_key] = PathDefinition(
            key=normalized_key, original_key=key, hidden=hidden
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
                level_key_original = ".".join(parts[: i + 1])
                # Normalize for registry lookup
                level_key = level_key_original.replace("-", "_")
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

    Attributes:
        base: The root directory for this PathTree
        rel: The relative path from base to current position
        hidden: Whether this directory should be hidden (prefixed with .)
        _registry: Internal registry of all path definitions

    Example:
        >>> builder = PathsBuilder(Path.home() / "dotfiles")
        >>> builder.add_path("dotfiles", hidden=True)
        >>> builder.add_path("dotfiles.starship", hidden=True)
        >>> builder.add_path("config", hidden=True)
        >>> paths = builder.build()
        >>>
        >>> # Create all registered directories at once
        >>> paths.create()
        >>>
        >>> # Navigate using attributes
        >>> paths.dotfiles.starship.path
        PosixPath('/home/user/.dotfiles/.starship')
        >>>
        >>> # Use as a path
        >>> str(paths.dotfiles)
        '/home/user/.dotfiles'
        >>>
        >>> # Access files
        >>> paths.dotfiles.starship.file("starship.toml")
        PosixPath('/home/user/.dotfiles/.starship/starship.toml')
        >>>
        >>> # Use in os functions (via __fspath__)
        >>> import shutil
        >>> shutil.copy("file.txt", paths.dotfiles)
    """

    _registry: dict[str, PathDefinition] = field(
        default_factory=dict, repr=False, compare=False
    )

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
                level_key_original = ".".join(parts[: i + 1])
                # Normalize for registry lookup
                level_key = level_key_original.replace("-", "_")
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

        Args:
            name: Directory name (trailing underscore removed for keywords)

        Returns:
            New ManagedPathTree instance pointing to the subdirectory

        Example:
            >>> paths = builder.build()
            >>> paths.dotfiles.starship
            ManagedPathTree(base=/home/user/dotfiles, rel=dotfiles/starship)
        """
        from filesystem_path_builder.pathtree import _clean_segment

        seg = _clean_segment(name)
        new_rel = self.rel / seg
        return ManagedPathTree(
            base=self.base,
            rel=new_rel,
            hidden=self._get_hidden_status(new_rel),
            _registry=self._registry,
        )

    def __getitem__(self, key: str | Path) -> "ManagedPathTree":
        """Navigate to subdirectory via bracket notation.

        Overrides PathTree's __getitem__ to return ManagedPathTree
        instead of PathTree, preserving the registry.

        Args:
            key: Directory name as string or Path

        Returns:
            New ManagedPathTree instance pointing to the subdirectory

        Example:
            >>> paths = builder.build()
            >>> paths["dotfiles"]["starship"]
            ManagedPathTree(base=/home/user/dotfiles, rel=dotfiles/starship)
        """
        new_rel = self.rel / str(key)
        return ManagedPathTree(
            base=self.base,
            rel=new_rel,
            hidden=self._get_hidden_status(new_rel),
            _registry=self._registry,
        )

    def __truediv__(self, other: str | Path) -> "ManagedPathTree":
        """Navigate to subdirectory via / operator.

        Overrides PathTree's __truediv__ to return ManagedPathTree
        instead of PathTree, preserving the registry.

        Args:
            other: Directory name as string or Path

        Returns:
            New ManagedPathTree instance pointing to the subdirectory

        Example:
            >>> paths = builder.build()
            >>> paths / "dotfiles" / "starship"
            ManagedPathTree(base=/home/user/dotfiles, rel=dotfiles/starship)
        """
        new_rel = self.rel / str(other)
        return ManagedPathTree(
            base=self.base,
            rel=new_rel,
            hidden=self._get_hidden_status(new_rel),
            _registry=self._registry,
        )

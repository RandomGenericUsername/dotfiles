"""
Filesystem Path Builder - Scalable path navigation and builder module.

This module provides three main components:

1. **PathTree**: Immutable, attribute-based directory navigation
2. **PathsBuilder**: Explicit path definition with hidden directory support
3. **ManagedPathTree**: PathTree with registry and create() capability

Quick Start:
    # Dynamic navigation with PathTree
    >>> from filesystem_path_builder import PathTree
    >>> paths = PathTree.from_str("~/dotfiles")
    >>> paths.config.nvim.path
    PosixPath('/home/user/dotfiles/config/nvim')

    # Explicit path building with PathsBuilder (recommended)
    >>> from filesystem_path_builder import PathsBuilder
    >>> builder = PathsBuilder(Path.home() / "dotfiles")
    >>> builder.add_path("dotfiles", hidden=True)
    >>> builder.add_path("scripts", hidden=False)
    >>> paths = builder.build()  # Returns ManagedPathTree
    >>> paths.create()  # Create all directories
    >>> paths.dotfiles.path  # Navigate to dotfiles

Public API:
    - PathTree: Main navigation class
    - PathsBuilder: Builder for explicit path definitions
    - ManagedPathTree: PathTree with registry and create() method
    - PathDefinition: Path definition dataclass
    - Segment: Type alias for path segments (str | Path)
"""

from filesystem_path_builder.builder import (
    ManagedPathTree,
    PathDefinition,
    PathsBuilder,
)
from filesystem_path_builder.pathtree import PathTree, Segment

__all__ = [
    "PathTree",
    "PathsBuilder",
    "ManagedPathTree",
    "PathDefinition",
    "Segment",
]

__version__ = "0.1.0"

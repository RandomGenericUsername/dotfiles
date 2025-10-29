"""
PathTree: Scalable and explicit directory navigation layer.

This module provides a clean, immutable way to navigate directory structures
through attribute chaining, making path management scalable and maintainable.

Example:
    >>> paths = PathTree.from_str("/tmp/dotfiles")
    >>> paths.scripts.modules.path
    PosixPath('/tmp/dotfiles/scripts/modules')
    >>> paths.scripts.modules.file("init.py")
    PosixPath('/tmp/dotfiles/scripts/modules/init.py')
    >>> paths.config.nvim.ensure_dir()
    PosixPath('/tmp/dotfiles/config/nvim')
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

Segment = Union[str, Path]


def _clean_segment(name: str) -> str:
    """Remove trailing underscore from Python reserved words.

    This allows using Python keywords as directory names by appending
    an underscore, which is then stripped.

    Example:
        >>> _clean_segment("class_")
        'class'
        >>> _clean_segment("normal")
        'normal'
    """
    return name[:-1] if name.endswith("_") else name


@dataclass(frozen=True, slots=True)
class PathTree:
    """Scalable and explicit directory navigation layer.

    PathTree provides an immutable, attribute-based interface for navigating
    directory structures. It separates directory navigation (via attributes)
    from file access (via .file() method), making code more explicit and
    maintainable.

    Attributes:
        base: The root directory for this PathTree
        rel: The relative path from base to current position
        hidden: Whether this directory should be hidden (prefixed with .)

    Example:
        >>> # Create PathTree from base directory
        >>> paths = PathTree.from_str("~/dotfiles")
        >>>
        >>> # Navigate using attributes
        >>> nvim_config = paths.config.nvim
        >>> nvim_config.path
        PosixPath('/home/user/dotfiles/config/nvim')
        >>>
        >>> # Access files explicitly
        >>> init_lua = nvim_config.file("init.lua")
        >>> init_lua
        PosixPath('/home/user/dotfiles/config/nvim/init.lua')
        >>>
        >>> # Create directories
        >>> nvim_config.ensure_dir()
        PosixPath('/home/user/dotfiles/config/nvim')
        >>>
        >>> # Check existence
        >>> if nvim_config.exists_dir():
        ...     print("Config exists!")
        >>>
        >>> # Navigate with variables or special characters
        >>> config_name = "nvim"
        >>> paths.config[config_name].path
        >>> paths["dotfiles-installer"].path  # Hyphens in names
    """

    base: Path
    rel: Path = Path()
    hidden: bool = False

    @staticmethod
    def from_str(base: str | Path, hidden: bool = False) -> PathTree:
        """Create PathTree from string or Path, expanding variables.

        Automatically expands environment variables ($HOME, $USER, etc.)
        and user home directory (~).

        Args:
            base: Base directory path as string or Path object
            hidden: Whether this directory should be hidden (prefixed with .)

        Returns:
            New PathTree instance rooted at the expanded base path

        Example:
            >>> PathTree.from_str("~/dotfiles")
            PathTree(base=/home/user/dotfiles, rel=.)
            >>> PathTree.from_str("$HOME/.config")
            PathTree(base=/home/user/.config, rel=.)
        """
        import os

        b = Path(os.path.expandvars(str(base))).expanduser()
        return PathTree(base=b, hidden=hidden)

    @property
    def path(self) -> Path:
        """Get the full path as a Path object.

        If hidden=True, applies dot prefix to the last component to match
        the actual directory name that will be created on disk.

        Returns:
            Complete path combining base and relative components, with
            dot prefix applied if hidden=True

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.foo.bar.path
            PosixPath('/tmp/foo/bar')
            >>> hidden = PathTree.from_str("/tmp", hidden=False)
            >>> hidden.foo.path  # hidden=False
            PosixPath('/tmp/foo')
            >>> hidden_dir = PathTree(base=Path("/tmp"), rel=Path("foo"), hidden=True)
            >>> hidden_dir.path  # hidden=True
            PosixPath('/tmp/.foo')
        """
        p = self.base / self.rel

        # Apply hidden flag by adding dot to last component
        if self.hidden and self.rel != Path():
            parts = p.parts
            parts = parts[:-1] + (f".{parts[-1]}",)
            p = Path(*parts)

        return p

    def resolve(self, strict: bool = False) -> Path:
        """Resolve the path to an absolute path.

        Args:
            strict: If True, raise FileNotFoundError if path doesn't exist

        Returns:
            Resolved absolute path

        Example:
            >>> paths = PathTree.from_str(".")
            >>> paths.resolve()
            PosixPath('/current/working/directory')
        """
        return self.path.resolve(strict=strict)

    def __getattr__(self, name: str) -> PathTree:
        """Navigate to subdirectory via attribute access.

        Args:
            name: Directory name (trailing underscore removed for keywords)

        Returns:
            New PathTree instance pointing to the subdirectory

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.foo.bar
            PathTree(base=/tmp, rel=foo/bar)
            >>> paths.class_  # Python keyword
            PathTree(base=/tmp, rel=class)
        """
        seg = _clean_segment(name)
        return PathTree(self.base, self.rel / seg, hidden=False)

    def __getitem__(self, key: Segment) -> PathTree:
        """Navigate to subdirectory via bracket notation.

        Useful for dynamic navigation or names with special characters.

        Args:
            key: Directory name as string or Path

        Returns:
            New PathTree instance pointing to the subdirectory

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths["foo-bar"]  # Hyphens not allowed in attributes
            PathTree(base=/tmp, rel=foo-bar)
            >>> config_name = "nvim"
            >>> paths[config_name]
            PathTree(base=/tmp, rel=nvim)
        """
        return PathTree(self.base, self.rel / str(key), hidden=False)

    def __truediv__(self, other: Segment) -> PathTree:
        """Navigate to subdirectory via / operator.

        Args:
            other: Directory name as string or Path

        Returns:
            New PathTree instance pointing to the subdirectory

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths / "foo" / "bar"
            PathTree(base=/tmp, rel=foo/bar)
        """
        return PathTree(self.base, self.rel / str(other), hidden=False)

    def up(self, n: int = 1) -> PathTree:
        """Navigate up n levels in the directory tree.

        Args:
            n: Number of levels to go up (default: 1)

        Returns:
            New PathTree instance pointing to parent directory

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> deep = paths.foo.bar.baz
            >>> deep.up(1)
            PathTree(base=/tmp, rel=foo/bar)
            >>> deep.up(2)
            PathTree(base=/tmp, rel=foo)
        """
        p = self.rel
        for _ in range(max(n, 0)):
            p = p.parent
        return PathTree(self.base, p)

    def file(self, filename: str | Path) -> Path:
        """Get path to a file in this directory.

        Args:
            filename: Name of the file

        Returns:
            Complete path to the file

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.config.nvim.file("init.lua")
            PosixPath('/tmp/config/nvim/init.lua')
        """
        return self.path / Path(filename)

    def ensure_dir(self) -> Path:
        """Create directory if it doesn't exist, return Path.

        Creates all parent directories as needed. Uses the .path property
        which already applies the dot prefix if hidden=True.

        Returns:
            Path to the created/existing directory

        Example:
            >>> paths = PathTree.from_str("/tmp/test")
            >>> paths.deep.nested.dir.ensure_dir()
            PosixPath('/tmp/test/deep/nested/dir')
            >>> hidden_dir = PathTree.from_str("/tmp/test", hidden=True)
            >>> hidden_dir.ensure_dir()
            PosixPath('/tmp/test/.test')
        """
        # Use .path property which already handles hidden flag
        p = self.path
        p.mkdir(parents=True, exist_ok=True)
        return p

    def ensure_file(
        self, filename: str | Path, touch_exists_ok: bool = True
    ) -> Path:
        """Create file and parent directories if they don't exist.

        Args:
            filename: Name of the file to create
            touch_exists_ok: If False, raise FileExistsError if file exists

        Returns:
            Path to the created/existing file

        Example:
            >>> paths = PathTree.from_str("/tmp/test")
            >>> paths.config.ensure_file("settings.toml")
            PosixPath('/tmp/test/config/settings.toml')
        """
        fp = self.file(filename)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.touch(exist_ok=touch_exists_ok)
        return fp

    def exists_dir(self) -> bool:
        """Check if directory exists.

        Returns:
            True if path exists and is a directory

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.existing_dir.exists_dir()
            True
            >>> paths.nonexistent.exists_dir()
            False
        """
        return self.path.is_dir()

    def exists_file(self, filename: str | Path) -> bool:
        """Check if file exists in this directory.

        Args:
            filename: Name of the file to check

        Returns:
            True if file exists

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.config.exists_file("settings.toml")
            True
        """
        return self.file(filename).is_file()

    def exists(self) -> bool:
        """Check if path exists (file or directory).

        Returns:
            True if path exists

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.existing.exists()
            True
        """
        return self.path.exists()

    def is_file(self) -> bool:
        """Check if path is a file.

        Returns:
            True if path exists and is a file

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.somefile_txt.is_file()
            True
        """
        return self.path.is_file()

    def is_dir(self) -> bool:
        """Check if path is a directory.

        Returns:
            True if path exists and is a directory

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.somedir.is_dir()
            True
        """
        return self.path.is_dir()

    def __str__(self) -> str:
        """String representation returns the path.

        Returns:
            String representation of the full path

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> str(paths.foo.bar)
            '/tmp/foo/bar'
        """
        return str(self.path)

    def __repr__(self) -> str:
        """Detailed representation for debugging.

        Returns:
            Detailed string showing base and relative components

        Example:
            >>> paths = PathTree.from_str("/tmp")
            >>> paths.foo.bar
            PathTree(base=/tmp, rel=foo/bar)
        """
        return f"PathTree(base={self.base!s}, rel={self.rel.as_posix()!s})"

    def __eq__(self, other: object) -> bool:
        """Compare PathTree objects or with Path objects.

        Args:
            other: PathTree or Path object to compare with

        Returns:
            True if paths are equal

        Example:
            >>> paths1 = PathTree.from_str("/tmp")
            >>> paths2 = PathTree.from_str("/tmp")
            >>> paths1.foo == paths2.foo
            True
            >>> paths1.foo.path == Path("/tmp/foo")
            True
        """
        if isinstance(other, PathTree):
            return self.path == other.path
        if isinstance(other, Path):
            return self.path == other
        return False

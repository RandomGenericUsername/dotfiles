"""Tests for PathTree class."""

import tempfile
from pathlib import Path

import pytest
from filesystem_path_builder import PathTree


class TestPathTreeCreation:
    """Test PathTree creation and initialization."""

    def test_from_str_basic(self):
        """Test basic PathTree creation from string."""
        paths = PathTree.from_str("/tmp/test")
        assert paths.base == Path("/tmp/test")
        assert paths.rel == Path()
        assert paths.hidden is False

    def test_from_str_with_tilde(self):
        """Test PathTree creation with ~ expansion."""
        paths = PathTree.from_str("~/test")
        assert paths.base == Path.home() / "test"

    def test_from_str_with_env_var(self, monkeypatch):
        """Test PathTree creation with environment variable."""
        monkeypatch.setenv("TEST_DIR", "/tmp/test")
        paths = PathTree.from_str("$TEST_DIR/subdir")
        assert paths.base == Path("/tmp/test/subdir")

    def test_from_str_hidden(self):
        """Test PathTree creation with hidden flag."""
        paths = PathTree.from_str("/tmp/test", hidden=True)
        assert paths.hidden is True


class TestPathTreeNavigation:
    """Test PathTree navigation methods."""

    def test_attribute_navigation(self):
        """Test navigation using attribute access."""
        paths = PathTree.from_str("/tmp")
        result = paths.foo.bar.baz
        assert result.path == Path("/tmp/foo/bar/baz")

    def test_bracket_navigation(self):
        """Test navigation using bracket notation."""
        paths = PathTree.from_str("/tmp")
        result = paths["foo"]["bar"]
        assert result.path == Path("/tmp/foo/bar")

    def test_slash_navigation(self):
        """Test navigation using / operator."""
        paths = PathTree.from_str("/tmp")
        result = paths / "foo" / "bar"
        assert result.path == Path("/tmp/foo/bar")

    def test_mixed_navigation(self):
        """Test mixed navigation methods."""
        paths = PathTree.from_str("/tmp")
        result = paths.foo["bar"] / "baz"
        assert result.path == Path("/tmp/foo/bar/baz")

    def test_keyword_navigation(self):
        """Test navigation with Python keywords."""
        paths = PathTree.from_str("/tmp")
        result = paths.class_
        assert result.path == Path("/tmp/class")

    def test_up_navigation(self):
        """Test navigating up the directory tree."""
        paths = PathTree.from_str("/tmp")
        deep = paths.foo.bar.baz
        assert deep.up(1).path == Path("/tmp/foo/bar")
        assert deep.up(2).path == Path("/tmp/foo")
        assert deep.up(3).path == Path("/tmp")


class TestPathTreeFiles:
    """Test PathTree file operations."""

    def test_file_method(self):
        """Test file() method."""
        paths = PathTree.from_str("/tmp")
        result = paths.config.file("settings.toml")
        assert result == Path("/tmp/config/settings.toml")

    def test_ensure_file(self):
        """Test ensure_file() creates file and directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = PathTree.from_str(tmpdir)
            result = paths.config.ensure_file("test.txt")
            assert result.exists()
            assert result.is_file()
            assert result.parent.exists()

    def test_exists_file(self):
        """Test exists_file() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = PathTree.from_str(tmpdir)
            test_file = Path(tmpdir) / "test.txt"
            test_file.touch()
            assert paths.exists_file("test.txt") is True
            assert paths.exists_file("nonexistent.txt") is False


class TestPathTreeDirectories:
    """Test PathTree directory operations."""

    def test_ensure_dir(self):
        """Test ensure_dir() creates directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = PathTree.from_str(tmpdir)
            result = paths.foo.bar.baz.ensure_dir()
            assert result.exists()
            assert result.is_dir()

    def test_ensure_dir_hidden(self):
        """Test ensure_dir() with hidden flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = PathTree(base=Path(tmpdir), rel=Path("test"), hidden=True)
            result = paths.ensure_dir()
            assert result.exists()
            assert result.name == ".test"

    def test_exists_dir(self):
        """Test exists_dir() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = PathTree.from_str(tmpdir)
            test_dir = Path(tmpdir) / "testdir"
            test_dir.mkdir()
            assert paths.testdir.exists_dir() is True
            assert paths.nonexistent.exists_dir() is False

    def test_is_dir(self):
        """Test is_dir() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = PathTree.from_str(tmpdir)
            test_dir = Path(tmpdir) / "testdir"
            test_dir.mkdir()
            assert paths.testdir.is_dir() is True
            assert paths.nonexistent.is_dir() is False


class TestPathTreeUtilities:
    """Test PathTree utility methods."""

    def test_path_property(self):
        """Test path property."""
        paths = PathTree.from_str("/tmp")
        assert paths.foo.bar.path == Path("/tmp/foo/bar")

    def test_resolve(self):
        """Test resolve() method."""
        paths = PathTree.from_str(".")
        result = paths.resolve()
        assert result.is_absolute()

    def test_str_representation(self):
        """Test __str__() method."""
        paths = PathTree.from_str("/tmp")
        assert str(paths.foo.bar) == "/tmp/foo/bar"

    def test_repr_representation(self):
        """Test __repr__() method."""
        paths = PathTree.from_str("/tmp")
        result = repr(paths.foo.bar)
        assert "PathTree" in result
        assert "/tmp" in result
        assert "foo/bar" in result

    def test_equality_with_pathtree(self):
        """Test equality comparison with another PathTree."""
        paths1 = PathTree.from_str("/tmp")
        paths2 = PathTree.from_str("/tmp")
        assert paths1.foo == paths2.foo

    def test_equality_with_path(self):
        """Test equality comparison with Path object."""
        paths = PathTree.from_str("/tmp")
        assert paths.foo.path == Path("/tmp/foo")

    def test_exists(self):
        """Test exists() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = PathTree.from_str(tmpdir)
            test_dir = Path(tmpdir) / "testdir"
            test_dir.mkdir()
            assert paths.testdir.exists() is True
            assert paths.nonexistent.exists() is False


class TestPathTreeImmutability:
    """Test PathTree immutability."""

    def test_frozen_dataclass(self):
        """Test that PathTree is immutable."""
        paths = PathTree.from_str("/tmp")
        # FrozenInstanceError
        with pytest.raises((AttributeError, Exception)):
            paths.base = Path("/other")

    def test_navigation_creates_new_instance(self):
        """Test that navigation creates new instances."""
        paths = PathTree.from_str("/tmp")
        child = paths.foo
        assert paths is not child
        assert paths.path != child.path

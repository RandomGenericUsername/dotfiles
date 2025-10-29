"""Tests for PathsBuilder class."""

import tempfile
from pathlib import Path

from filesystem_path_builder import (
    PathDefinition,
    PathNamespace,
    PathsBuilder,
    PathTree,
)


class TestPathDefinition:
    """Test PathDefinition dataclass."""

    def test_creation(self):
        """Test PathDefinition creation."""
        pd = PathDefinition(key="foo.bar.baz", hidden=True)
        assert pd.key == "foo.bar.baz"
        assert pd.hidden is True

    def test_get_parts(self):
        """Test get_parts() method."""
        pd = PathDefinition(key="foo.bar.baz", hidden=False)
        assert pd.get_parts() == ["foo", "bar", "baz"]

    def test_get_parts_single(self):
        """Test get_parts() with single part."""
        pd = PathDefinition(key="foo", hidden=False)
        assert pd.get_parts() == ["foo"]

    def test_default_hidden(self):
        """Test default hidden value is False."""
        pd = PathDefinition(key="foo")
        assert pd.hidden is False


class TestPathNamespace:
    """Test PathNamespace class."""

    def test_creation(self):
        """Test PathNamespace creation."""
        ns = PathNamespace()
        assert isinstance(ns, PathNamespace)

    def test_attribute_setting(self):
        """Test setting attributes on PathNamespace."""
        ns = PathNamespace()
        paths = PathTree.from_str("/tmp")
        ns.foo = paths
        assert ns.foo == paths

    def test_attribute_access(self):
        """Test accessing attributes on PathNamespace."""
        ns = PathNamespace()
        paths = PathTree.from_str("/tmp")
        ns.foo = paths
        assert hasattr(ns, "foo")
        assert ns.foo.path == Path("/tmp")


class TestPathsBuilder:
    """Test PathsBuilder class."""

    def test_creation(self):
        """Test PathsBuilder creation."""
        builder = PathsBuilder(Path("/tmp"))
        assert builder.root == Path("/tmp")
        assert builder.definitions == {}

    def test_add_path_basic(self):
        """Test adding a basic path."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo")
        assert "foo" in builder.definitions
        assert builder.definitions["foo"].key == "foo"
        assert builder.definitions["foo"].hidden is False

    def test_add_path_hidden(self):
        """Test adding a hidden path."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo", hidden=True)
        assert builder.definitions["foo"].hidden is True

    def test_add_path_nested(self):
        """Test adding nested paths."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo.bar.baz")
        assert "foo.bar.baz" in builder.definitions

    def test_add_path_method_chaining(self):
        """Test method chaining with add_path."""
        builder = PathsBuilder(Path("/tmp"))
        result = builder.add_path("foo").add_path("bar")
        assert result is builder
        assert "foo" in builder.definitions
        assert "bar" in builder.definitions

    def test_build_basic(self):
        """Test building basic namespace."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo")
        builder.add_path("bar")
        ns = builder.build()
        assert hasattr(ns, "foo")
        assert hasattr(ns, "bar")
        assert ns.foo.path == Path("/tmp/foo")
        assert ns.bar.path == Path("/tmp/bar")

    def test_build_nested(self):
        """Test building nested paths."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo")
        builder.add_path("foo.bar")
        builder.add_path("foo.bar.baz")
        ns = builder.build()
        assert ns.foo.path == Path("/tmp/foo")
        assert ns.foo.bar.path == Path("/tmp/foo/bar")
        assert ns.foo.bar.baz.path == Path("/tmp/foo/bar/baz")

    def test_build_hidden(self):
        """Test building with hidden paths."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo", hidden=True)
        ns = builder.build()
        assert ns.foo.hidden is True

    def test_build_mixed_hidden(self):
        """Test building with mixed hidden/visible paths."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo", hidden=True)
        builder.add_path("bar", hidden=False)
        ns = builder.build()
        assert ns.foo.hidden is True
        assert ns.bar.hidden is False

    def test_build_complex_structure(self):
        """Test building complex directory structure."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("dotfiles", hidden=True)
        builder.add_path("config", hidden=True)
        builder.add_path("scripts", hidden=False)

        ns = builder.build()

        # Only the explicitly defined paths have hidden flag
        assert ns.dotfiles.hidden is True
        assert ns.config.hidden is True
        assert ns.scripts.hidden is False

        # Paths are correct
        assert ns.dotfiles.path == Path("/tmp/dotfiles")
        assert ns.scripts.path == Path("/tmp/scripts")


class TestPathsBuilderIntegration:
    """Test PathsBuilder integration with filesystem."""

    def test_ensure_dir_from_builder(self):
        """Test ensure_dir() on paths from builder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = PathsBuilder(Path(tmpdir))
            builder.add_path("foo.bar.baz")
            ns = builder.build()

            result = ns.foo.bar.baz.ensure_dir()
            assert result.exists()
            assert result.is_dir()

    def test_ensure_dir_hidden_from_builder(self):
        """Test ensure_dir() with hidden paths from builder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = PathsBuilder(Path(tmpdir))
            builder.add_path("dotfiles", hidden=True)
            ns = builder.build()

            result = ns.dotfiles.ensure_dir()
            assert result.exists()
            # Only the last component gets the dot prefix
            assert result.name == ".dotfiles"
            assert result.parent == Path(tmpdir)

    def test_file_operations_from_builder(self):
        """Test file operations on paths from builder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = PathsBuilder(Path(tmpdir))
            builder.add_path("config")
            ns = builder.build()

            file_path = ns.config.ensure_file("settings.toml")
            assert file_path.exists()
            assert file_path.is_file()

    def test_navigation_from_builder(self):
        """Test navigation on paths from builder."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo")
        ns = builder.build()

        # Can still navigate further from builder-created paths
        result = ns.foo.bar.baz
        assert result.path == Path("/tmp/foo/bar/baz")


class TestPathsBuilderEdgeCases:
    """Test PathsBuilder edge cases."""

    def test_empty_builder(self):
        """Test building with no paths added."""
        builder = PathsBuilder(Path("/tmp"))
        ns = builder.build()
        assert isinstance(ns, PathNamespace)

    def test_duplicate_paths(self):
        """Test adding duplicate paths (should overwrite)."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo", hidden=False)
        builder.add_path("foo", hidden=True)
        ns = builder.build()
        assert ns.foo.hidden is True

    def test_overlapping_paths(self):
        """Test adding overlapping paths."""
        builder = PathsBuilder(Path("/tmp"))
        builder.add_path("foo.bar")
        builder.add_path("foo.bar.baz")
        builder.add_path("foo")
        ns = builder.build()

        # First definition wins for top-level attribute (due to `if not hasattr`)
        # "foo.bar" was added first, so ns.foo points to /tmp/foo/bar
        assert ns.foo.path == Path("/tmp/foo/bar")
        # Can navigate from there
        assert ns.foo.baz.path == Path("/tmp/foo/bar/baz")

    def test_root_with_tilde(self):
        """Test builder with ~ in root."""
        builder = PathsBuilder(Path("~/test").expanduser())
        builder.add_path("foo")
        ns = builder.build()
        assert ns.foo.path == Path.home() / "test" / "foo"

    def test_create_all_directories(self):
        """Test create() method creates all defined directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = PathsBuilder(Path(tmpdir))
            builder.add_path("nvim")
            builder.add_path("nvim.lua")
            builder.add_path("nvim.lua.plugins")
            builder.add_path("starship")

            created = builder.create()

            # All directories should be created
            assert len(created) == 4
            assert all(p.exists() for p in created)
            assert all(p.is_dir() for p in created)

            # Check specific paths
            assert (Path(tmpdir) / "nvim").exists()
            assert (Path(tmpdir) / "nvim" / "lua").exists()
            assert (Path(tmpdir) / "nvim" / "lua" / "plugins").exists()
            assert (Path(tmpdir) / "starship").exists()

    def test_create_with_hidden_directories(self):
        """Test create() method with hidden directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = PathsBuilder(Path(tmpdir))
            builder.add_path("dotfiles", hidden=True)
            builder.add_path("config", hidden=True)
            builder.add_path("scripts", hidden=False)

            created = builder.create()

            # All directories should be created
            assert len(created) == 3
            assert all(p.exists() for p in created)

            # Check hidden directories have dot prefix
            assert (Path(tmpdir) / ".dotfiles").exists()
            assert (Path(tmpdir) / ".config").exists()
            assert (Path(tmpdir) / "scripts").exists()

    def test_create_returns_paths(self):
        """Test create() returns list of created paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = PathsBuilder(Path(tmpdir))
            builder.add_path("foo")
            builder.add_path("bar")

            created = builder.create()

            assert isinstance(created, list)
            assert len(created) == 2
            assert all(isinstance(p, Path) for p in created)

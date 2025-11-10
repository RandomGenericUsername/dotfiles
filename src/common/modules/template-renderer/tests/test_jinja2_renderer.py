"""Tests for Jinja2 template renderer."""

from pathlib import Path

import pytest

from dotfiles_template_renderer import (
    Jinja2Renderer,
    MissingVariableError,
    RenderConfig,
    TemplateNotFoundError,
    TemplateRenderError,
)
from dotfiles_template_renderer.core.types import TemplateContext


class TestJinja2RendererInitialization:
    """Tests for Jinja2Renderer initialization."""

    def test_renderer_can_be_instantiated(self, temp_template_dir: Path):
        """Test that renderer can be instantiated."""
        renderer = Jinja2Renderer(temp_template_dir)
        assert renderer is not None

    def test_renderer_with_string_path(self, temp_template_dir: Path):
        """Test renderer initialization with string path."""
        renderer = Jinja2Renderer(str(temp_template_dir))
        assert renderer.template_dir == temp_template_dir

    def test_renderer_with_path_object(self, temp_template_dir: Path):
        """Test renderer initialization with Path object."""
        renderer = Jinja2Renderer(temp_template_dir)
        assert renderer.template_dir == temp_template_dir

    def test_renderer_with_config(
        self, temp_template_dir: Path, strict_config: RenderConfig
    ):
        """Test renderer initialization with config."""
        renderer = Jinja2Renderer(temp_template_dir, strict_config)
        assert renderer.config == strict_config

    def test_renderer_with_nonexistent_directory(self, tmp_path: Path):
        """Test renderer raises error for nonexistent directory."""
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            Jinja2Renderer(nonexistent)

    def test_renderer_default_config(self, temp_template_dir: Path):
        """Test renderer creates default config if none provided."""
        renderer = Jinja2Renderer(temp_template_dir)
        assert renderer.config is not None
        assert isinstance(renderer.config, RenderConfig)


class TestJinja2RendererBasicRendering:
    """Tests for basic template rendering."""

    def test_render_simple_template(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test rendering a simple template."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)
        result = renderer.render(template_name, {"name": "World"})
        assert result == "Hello World!"

    def test_render_with_dict_variables(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test rendering with variables as dict."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)
        result = renderer.render(template_name, {"name": "Alice"})
        assert result == "Hello Alice!"

    def test_render_with_kwargs(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test rendering with variables as kwargs."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)
        result = renderer.render(template_name, name="Bob")
        assert result == "Hello Bob!"

    def test_render_with_dict_and_kwargs(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test rendering with both dict and kwargs (kwargs override)."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)
        result = renderer.render(template_name, {"name": "Alice"}, name="Bob")
        assert result == "Hello Bob!"

    def test_render_complex_template(
        self, temp_template_dir: Path, complex_template: tuple[Path, str]
    ):
        """Test rendering a complex template with multiple variables."""
        _, template_name = complex_template
        renderer = Jinja2Renderer(temp_template_dir)
        result = renderer.render(
            template_name,
            {
                "app_name": "MyApp",
                "version": "2.0.0",
                "debug": "true",
                "features": ["auth", "api", "ui"],
            },
        )
        assert "MyApp" in result
        assert "2.0.0" in result
        assert "auth" in result
        assert "api" in result
        assert "ui" in result

    def test_render_empty_template(
        self, temp_template_dir: Path, empty_template: tuple[Path, str]
    ):
        """Test rendering an empty template."""
        _, template_name = empty_template
        renderer = Jinja2Renderer(temp_template_dir)
        result = renderer.render(template_name, {})
        assert result == ""

    def test_render_template_with_no_variables(self, temp_template_dir: Path):
        """Test rendering a template that requires no variables."""
        template_name = "static.j2"
        (temp_template_dir / template_name).write_text("Static content")
        renderer = Jinja2Renderer(temp_template_dir)
        result = renderer.render(template_name, {})
        assert result == "Static content"


class TestJinja2RendererStrictMode:
    """Tests for strict mode validation."""

    def test_strict_mode_raises_on_missing_variable(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test strict mode raises error for missing variables."""
        _, template_name = simple_template
        config = RenderConfig(strict_mode=True)
        renderer = Jinja2Renderer(temp_template_dir, config)

        with pytest.raises(MissingVariableError) as exc_info:
            renderer.render(template_name, {})

        assert "name" in str(exc_info.value)

    def test_non_strict_mode_allows_missing_variables(
        self, temp_template_dir: Path, template_with_defaults: tuple[Path, str]
    ):
        """Test non-strict mode allows missing variables with defaults."""
        _, template_name = template_with_defaults
        config = RenderConfig(strict_mode=False)
        renderer = Jinja2Renderer(temp_template_dir, config)

        result = renderer.render(template_name, {"name": "test"})
        assert "test" in result
        assert "8080" in result  # Default value
        assert "localhost" in result  # Default value

    def test_strict_mode_validates_before_rendering(
        self, temp_template_dir: Path, complex_template: tuple[Path, str]
    ):
        """Test strict mode validates variables before rendering."""
        _, template_name = complex_template
        config = RenderConfig(strict_mode=True)
        renderer = Jinja2Renderer(temp_template_dir, config)

        with pytest.raises(MissingVariableError) as exc_info:
            renderer.render(template_name, {"app_name": "test"})

        error = exc_info.value
        assert "version" in str(error) or "debug" in str(error)


class TestJinja2RendererErrorHandling:
    """Tests for error handling."""

    def test_render_nonexistent_template(self, temp_template_dir: Path):
        """Test rendering a nonexistent template raises error."""
        # Use non-strict mode to bypass validation and hit the template loading
        config = RenderConfig(strict_mode=False)
        renderer = Jinja2Renderer(temp_template_dir, config)

        with pytest.raises(TemplateNotFoundError) as exc_info:
            renderer.render("nonexistent.j2", {})

        assert "nonexistent.j2" in str(exc_info.value)

    def test_render_template_with_syntax_error(
        self,
        temp_template_dir: Path,
        template_with_syntax_error: tuple[Path, str],
    ):
        """Test rendering a template with syntax errors."""
        _, template_name = template_with_syntax_error
        renderer = Jinja2Renderer(temp_template_dir)

        with pytest.raises(TemplateRenderError):
            renderer.render(template_name, {"name": "test"})

    def test_template_not_found_error_includes_search_paths(
        self, temp_template_dir: Path
    ):
        """Test TemplateNotFoundError includes search paths."""
        # Use non-strict mode to bypass validation and hit the template loading
        config = RenderConfig(strict_mode=False)
        renderer = Jinja2Renderer(temp_template_dir, config)

        with pytest.raises(TemplateNotFoundError) as exc_info:
            renderer.render("missing.j2", {})

        error = exc_info.value
        assert error.template_name == "missing.j2"
        assert len(error.search_paths) > 0


class TestJinja2RendererValidation:
    """Tests for template validation."""

    def test_validate_template_with_all_variables(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test validation passes when all variables provided."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)

        result = renderer.validate(template_name, {"name": "test"})
        assert result.is_valid
        assert len(result.missing_variables) == 0

    def test_validate_template_with_missing_variables(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test validation fails when variables are missing."""
        _, template_name = simple_template
        config = RenderConfig(strict_mode=True)
        renderer = Jinja2Renderer(temp_template_dir, config)

        result = renderer.validate(template_name, {})
        assert not result.is_valid
        assert "name" in result.missing_variables

    def test_validate_template_with_unused_variables(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test validation detects unused variables."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)

        result = renderer.validate(
            template_name, {"name": "test", "unused": "value"}
        )
        assert result.is_valid  # Still valid, just has warnings
        assert "unused" in result.unused_variables

    def test_validate_nonexistent_template(self, temp_template_dir: Path):
        """Test validation of nonexistent template."""
        renderer = Jinja2Renderer(temp_template_dir)

        result = renderer.validate("nonexistent.j2", {})
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_complex_template(
        self, temp_template_dir: Path, complex_template: tuple[Path, str]
    ):
        """Test validation of complex template."""
        _, template_name = complex_template
        renderer = Jinja2Renderer(temp_template_dir)

        result = renderer.validate(
            template_name,
            {
                "app_name": "test",
                "version": "1.0",
                "debug": True,
                "features": [],
            },
        )
        assert result.is_valid
        assert len(result.missing_variables) == 0


class TestJinja2RendererTemplateIntrospection:
    """Tests for template introspection methods."""

    def test_get_template_variables(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test getting variables from a template."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)

        variables = renderer.get_template_variables(template_name)
        assert "name" in variables

    def test_get_template_variables_complex(
        self, temp_template_dir: Path, complex_template: tuple[Path, str]
    ):
        """Test getting variables from a complex template."""
        _, template_name = complex_template
        renderer = Jinja2Renderer(temp_template_dir)

        variables = renderer.get_template_variables(template_name)
        assert "app_name" in variables
        assert "version" in variables
        assert "debug" in variables
        assert "features" in variables

    def test_get_template_variables_nonexistent(self, temp_template_dir: Path):
        """Test getting variables from nonexistent template."""
        renderer = Jinja2Renderer(temp_template_dir)

        with pytest.raises(TemplateNotFoundError):
            renderer.get_template_variables("nonexistent.j2")

    def test_get_available_templates(
        self, temp_template_dir: Path, multiple_templates: Path
    ):
        """Test getting list of available templates."""
        renderer = Jinja2Renderer(temp_template_dir)

        templates = renderer.get_available_templates()
        assert "template1.j2" in templates
        assert "template2.jinja" in templates
        assert "template3.jinja2" in templates
        assert "not_a_template.txt" not in templates  # Wrong extension

    def test_get_available_templates_empty_directory(
        self, temp_template_dir: Path
    ):
        """Test getting templates from empty directory."""
        renderer = Jinja2Renderer(temp_template_dir)

        templates = renderer.get_available_templates()
        assert len(templates) == 0

    def test_get_template_info(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test getting template info."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)

        info = renderer.get_template_info(template_name)
        assert info.name == template_name
        assert info.path.exists()
        assert info.size > 0
        assert "name" in info.required_variables

    def test_get_template_info_with_description(
        self,
        temp_template_dir: Path,
        template_with_description: tuple[Path, str],
    ):
        """Test getting template info with description."""
        _, template_name = template_with_description
        renderer = Jinja2Renderer(temp_template_dir)

        info = renderer.get_template_info(template_name)
        assert info.description is not None
        assert "sample configuration" in info.description.lower()

    def test_get_template_info_nonexistent(self, temp_template_dir: Path):
        """Test getting info for nonexistent template."""
        renderer = Jinja2Renderer(temp_template_dir)

        with pytest.raises(TemplateNotFoundError):
            renderer.get_template_info("nonexistent.j2")


class TestJinja2RendererCustomFilters:
    """Tests for custom filters."""

    def test_render_with_custom_filter(
        self, temp_template_dir: Path, custom_filter_config: RenderConfig
    ):
        """Test rendering with custom filters."""
        template_name = "custom_filter.j2"
        (temp_template_dir / template_name).write_text(
            "{{ text | uppercase }}"
        )

        renderer = Jinja2Renderer(temp_template_dir, custom_filter_config)
        result = renderer.render(template_name, {"text": "hello"})
        assert result == "HELLO"

    def test_render_with_multiple_custom_filters(
        self, temp_template_dir: Path, custom_filter_config: RenderConfig
    ):
        """Test rendering with multiple custom filters."""
        template_name = "multi_filter.j2"
        (temp_template_dir / template_name).write_text(
            "{{ text | uppercase | reverse }}"
        )

        renderer = Jinja2Renderer(temp_template_dir, custom_filter_config)
        result = renderer.render(template_name, {"text": "hello"})
        assert result == "OLLEH"


class TestJinja2RendererCustomTests:
    """Tests for custom tests."""

    def test_render_with_custom_test(
        self, temp_template_dir: Path, custom_test_config: RenderConfig
    ):
        """Test rendering with custom tests."""
        template_name = "custom_test.j2"
        (temp_template_dir / template_name).write_text(
            "{% if number is even %}even{% else %}odd{% endif %}"
        )

        renderer = Jinja2Renderer(temp_template_dir, custom_test_config)
        result = renderer.render(template_name, {"number": 4})
        assert result == "even"


class TestJinja2RendererCustomGlobals:
    """Tests for custom global variables."""

    def test_render_with_custom_globals(
        self, temp_template_dir: Path, custom_globals_config: RenderConfig
    ):
        """Test rendering with custom global variables."""
        template_name = "custom_globals.j2"
        (temp_template_dir / template_name).write_text(
            "Version: {{ app_version }}, Port: {{ default_port }}"
        )

        renderer = Jinja2Renderer(temp_template_dir, custom_globals_config)
        result = renderer.render(template_name, {})
        assert "1.0.0" in result
        assert "8080" in result


class TestJinja2RendererContextRendering:
    """Tests for rendering with TemplateContext."""

    def test_render_from_context(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test rendering using TemplateContext."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)

        context = TemplateContext(
            template_name=template_name,
            variables={"name": "Context"},
        )
        result = renderer.render_from_context(context)
        assert result == "Hello Context!"

    def test_render_from_context_with_config_override(
        self, temp_template_dir: Path, simple_template: tuple[Path, str]
    ):
        """Test rendering with context config override."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)

        context = TemplateContext(
            template_name=template_name,
            variables={"name": "Test"},
            config=RenderConfig(strict_mode=False),
        )
        result = renderer.render_from_context(context)
        assert result == "Hello Test!"


class TestJinja2RendererFileOutput:
    """Tests for rendering to file."""

    def test_render_to_file(
        self,
        temp_template_dir: Path,
        simple_template: tuple[Path, str],
        tmp_path: Path,
    ):
        """Test rendering template to file."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)

        output_path = tmp_path / "output.txt"
        renderer.render_to_file(template_name, output_path, {"name": "File"})

        assert output_path.exists()
        assert output_path.read_text() == "Hello File!"

    def test_render_to_file_creates_parent_directories(
        self,
        temp_template_dir: Path,
        simple_template: tuple[Path, str],
        tmp_path: Path,
    ):
        """Test rendering to file creates parent directories."""
        _, template_name = simple_template
        renderer = Jinja2Renderer(temp_template_dir)

        output_path = tmp_path / "nested" / "dir" / "output.txt"
        renderer.render_to_file(template_name, output_path, {"name": "Nested"})

        assert output_path.exists()
        assert output_path.read_text() == "Hello Nested!"


class TestJinja2RendererSpecialCases:
    """Tests for special cases and edge cases."""

    def test_render_with_special_characters(
        self,
        temp_template_dir: Path,
        template_with_special_chars: tuple[Path, str],
    ):
        """Test rendering with special characters."""
        _, template_name = template_with_special_chars
        renderer = Jinja2Renderer(temp_template_dir)

        result = renderer.render(
            template_name,
            {
                "emoji": "😀",
                "unicode_text": "こんにちは",
                "symbols": "!@#$%^&*()",
            },
        )
        assert "😀" in result
        assert "こんにちは" in result
        assert "!@#$%^&*()" in result

    def test_render_template_with_inheritance(
        self,
        temp_template_dir: Path,
        template_with_inheritance: tuple[Path, str, str],
    ):
        """Test rendering template with inheritance."""
        _, base_name, child_name = template_with_inheritance
        renderer = Jinja2Renderer(temp_template_dir)

        result = renderer.render(
            child_name,
            {
                "title": "Test Page",
                "heading": "Welcome",
                "content": "This is a test",
            },
        )
        assert "Test Page" in result
        assert "Welcome" in result
        assert "This is a test" in result
        assert "<!DOCTYPE html>" in result

    def test_render_nested_template(
        self, temp_template_dir: Path, nested_template_dir: Path
    ):
        """Test rendering template from nested directory."""
        renderer = Jinja2Renderer(temp_template_dir)

        result = renderer.render("configs/app.j2", {"app_name": "MyApp"})
        assert "MyApp" in result

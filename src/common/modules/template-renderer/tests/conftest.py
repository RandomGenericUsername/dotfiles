"""Shared fixtures for template-renderer tests."""

from pathlib import Path
from typing import Any

import pytest

from dotfiles_template_renderer import RenderConfig


@pytest.fixture
def temp_template_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for templates."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return template_dir


@pytest.fixture
def simple_template(temp_template_dir: Path) -> tuple[Path, str]:
    """Create a simple template file."""
    template_name = "simple.j2"
    template_path = temp_template_dir / template_name
    template_content = "Hello {{ name }}!"
    template_path.write_text(template_content)
    return template_path, template_name


@pytest.fixture
def complex_template(temp_template_dir: Path) -> tuple[Path, str]:
    """Create a complex template with multiple variables."""
    template_name = "complex.j2"
    template_path = temp_template_dir / template_name
    template_content = """
# Configuration for {{ app_name }}
version: {{ version }}
debug: {{ debug }}
{% if features %}
features:
{% for feature in features %}
  - {{ feature }}
{% endfor %}
{% endif %}
""".strip()
    template_path.write_text(template_content)
    return template_path, template_name


@pytest.fixture
def template_with_defaults(temp_template_dir: Path) -> tuple[Path, str]:
    """Create a template with default values."""
    template_name = "defaults.j2"
    template_path = temp_template_dir / template_name
    template_content = """
name: {{ name }}
port: {{ port | default(8080) }}
host: {{ host | default('localhost') }}
""".strip()
    template_path.write_text(template_content)
    return template_path, template_name


@pytest.fixture
def template_with_description(temp_template_dir: Path) -> tuple[Path, str]:
    """Create a template with a description comment."""
    template_name = "described.j2"
    template_path = temp_template_dir / template_name
    template_content = """{# This is a sample configuration template #}
server: {{ server }}
port: {{ port }}
""".strip()
    template_path.write_text(template_content)
    return template_path, template_name


@pytest.fixture
def nested_template_dir(temp_template_dir: Path) -> Path:
    """Create nested template directories."""
    nested_dir = temp_template_dir / "configs"
    nested_dir.mkdir()

    # Create template in nested directory
    template_path = nested_dir / "app.j2"
    template_path.write_text("app: {{ app_name }}")

    return temp_template_dir


@pytest.fixture
def default_config() -> RenderConfig:
    """Create a default render configuration."""
    return RenderConfig()


@pytest.fixture
def strict_config() -> RenderConfig:
    """Create a strict render configuration."""
    return RenderConfig(strict_mode=True)


@pytest.fixture
def non_strict_config() -> RenderConfig:
    """Create a non-strict render configuration."""
    return RenderConfig(strict_mode=False)


@pytest.fixture
def custom_filter_config() -> RenderConfig:
    """Create a config with custom filters."""

    def uppercase_filter(text: str) -> str:
        return text.upper()

    def reverse_filter(text: str) -> str:
        return text[::-1]

    return RenderConfig(
        custom_filters={
            "uppercase": uppercase_filter,
            "reverse": reverse_filter,
        }
    )


@pytest.fixture
def custom_test_config() -> RenderConfig:
    """Create a config with custom tests."""

    def is_even(n: int) -> bool:
        return n % 2 == 0

    return RenderConfig(
        custom_tests={
            "even": is_even,
        }
    )


@pytest.fixture
def custom_globals_config() -> RenderConfig:
    """Create a config with custom global variables."""
    return RenderConfig(
        custom_globals={
            "app_version": "1.0.0",
            "default_port": 8080,
        }
    )


@pytest.fixture
def sample_variables() -> dict[str, Any]:
    """Create sample variables for testing."""
    return {
        "name": "test_app",
        "version": "1.0.0",
        "debug": True,
        "port": 8080,
        "host": "localhost",
    }


@pytest.fixture
def template_with_syntax_error(temp_template_dir: Path) -> tuple[Path, str]:
    """Create a template with syntax errors."""
    template_name = "syntax_error.j2"
    template_path = temp_template_dir / template_name
    template_content = "Hello {{ name"  # Missing closing braces
    template_path.write_text(template_content)
    return template_path, template_name


@pytest.fixture
def template_with_undefined_var(temp_template_dir: Path) -> tuple[Path, str]:
    """Create a template that uses undefined variables."""
    template_name = "undefined.j2"
    template_path = temp_template_dir / template_name
    template_content = "Value: {{ undefined_variable }}"
    template_path.write_text(template_content)
    return template_path, template_name


@pytest.fixture
def multiple_templates(temp_template_dir: Path) -> Path:
    """Create multiple template files."""
    templates = {
        "template1.j2": "Template 1: {{ var1 }}",
        "template2.jinja": "Template 2: {{ var2 }}",
        "template3.jinja2": "Template 3: {{ var3 }}",
        "not_a_template.txt": "This is not a template",
    }

    for name, content in templates.items():
        (temp_template_dir / name).write_text(content)

    return temp_template_dir


@pytest.fixture
def template_with_special_chars(temp_template_dir: Path) -> tuple[Path, str]:
    """Create a template with special characters."""
    template_name = "special.j2"
    template_path = temp_template_dir / template_name
    template_content = """
# Special characters test
emoji: {{ emoji }}
unicode: {{ unicode_text }}
symbols: {{ symbols }}
""".strip()
    template_path.write_text(template_content)
    return template_path, template_name


@pytest.fixture
def empty_template(temp_template_dir: Path) -> tuple[Path, str]:
    """Create an empty template file."""
    template_name = "empty.j2"
    template_path = temp_template_dir / template_name
    template_path.write_text("")
    return template_path, template_name


@pytest.fixture
def template_with_inheritance(
    temp_template_dir: Path,
) -> tuple[Path, str, str]:
    """Create templates with inheritance (base and child)."""
    # Base template
    base_name = "base.j2"
    base_path = temp_template_dir / base_name
    base_content = """
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{{ title }}{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
""".strip()
    base_path.write_text(base_content)

    # Child template
    child_name = "child.j2"
    child_path = temp_template_dir / child_name
    child_content = """
{% extends "base.j2" %}
{% block content %}
<h1>{{ heading }}</h1>
<p>{{ content }}</p>
{% endblock %}
""".strip()
    child_path.write_text(child_content)

    return temp_template_dir, base_name, child_name

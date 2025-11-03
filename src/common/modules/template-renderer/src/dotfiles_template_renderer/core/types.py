"""Core types for template rendering."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RenderConfig:
    """Configuration for template rendering."""

    strict_mode: bool = True
    """Fail if required variables are missing"""

    autoescape: bool = False
    """Enable autoescaping for HTML/XML templates"""

    trim_blocks: bool = True
    """Remove first newline after template tag"""

    lstrip_blocks: bool = True
    """Strip leading spaces/tabs from start of line to block"""

    keep_trailing_newline: bool = True
    """Keep trailing newline at end of template"""

    undefined_behavior: str = "strict"
    """How to handle undefined variables: 'strict', 'default', 'debug'"""

    custom_filters: dict[str, Any] = field(default_factory=dict)
    """Custom Jinja2 filters to add"""

    custom_tests: dict[str, Any] = field(default_factory=dict)
    """Custom Jinja2 tests to add"""

    custom_globals: dict[str, Any] = field(default_factory=dict)
    """Custom global variables/functions"""


@dataclass
class TemplateContext:
    """Context for template rendering."""

    template_name: str
    """Name of the template file"""

    variables: dict[str, Any]
    """Variables to use in template rendering"""

    config: RenderConfig = field(default_factory=RenderConfig)
    """Rendering configuration"""


@dataclass
class ValidationResult:
    """Result of template validation."""

    is_valid: bool
    """Whether the template is valid"""

    missing_variables: list[str] = field(default_factory=list)
    """Variables required by template but not provided"""

    unused_variables: list[str] = field(default_factory=list)
    """Variables provided but not used in template"""

    required_variables: list[str] = field(default_factory=list)
    """All variables required by the template"""

    errors: list[str] = field(default_factory=list)
    """Validation error messages"""

    warnings: list[str] = field(default_factory=list)
    """Validation warning messages"""


@dataclass
class TemplateInfo:
    """Information about a template."""

    name: str
    """Template name"""

    path: Path
    """Full path to template file"""

    size: int
    """File size in bytes"""

    required_variables: list[str] = field(default_factory=list)
    """Variables required by this template"""

    optional_variables: list[str] = field(default_factory=list)
    """Variables with default values"""

    description: str | None = None
    """Template description (from docstring or metadata)"""

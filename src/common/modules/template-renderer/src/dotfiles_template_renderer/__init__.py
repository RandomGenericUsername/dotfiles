"""Template rendering module - agnostic template rendering with Jinja2."""

from .core import (
    InvalidVariableError,
    MissingVariableError,
    RenderConfig,
    TemplateContext,
    TemplateError,
    TemplateInfo,
    TemplateNotFoundError,
    TemplateRenderer,
    TemplateRenderError,
    ValidationError,
    ValidationResult,
)
from .renderers import Jinja2Renderer
from .validators import (
    extract_jinja2_variables,
    validate_variable_types,
    validate_variables,
)

__all__ = [
    # Core
    "TemplateRenderer",
    "RenderConfig",
    "TemplateContext",
    "TemplateInfo",
    "ValidationResult",
    # Renderers
    "Jinja2Renderer",
    # Exceptions
    "TemplateError",
    "TemplateNotFoundError",
    "TemplateRenderError",
    "ValidationError",
    "MissingVariableError",
    "InvalidVariableError",
    # Validators
    "extract_jinja2_variables",
    "validate_variables",
    "validate_variable_types",
]

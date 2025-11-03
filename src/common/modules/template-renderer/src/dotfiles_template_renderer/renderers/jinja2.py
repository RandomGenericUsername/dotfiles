"""Jinja2 template renderer implementation."""

from pathlib import Path
from typing import Any

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateNotFound,
    UndefinedError,
)

from ..core.base import TemplateRenderer
from ..core.exceptions import (
    MissingVariableError,
    TemplateNotFoundError,
    TemplateRenderError,
)
from ..core.types import RenderConfig, TemplateInfo, ValidationResult
from ..validators import extract_jinja2_variables, validate_variables


class Jinja2Renderer(TemplateRenderer):
    """Jinja2-based template renderer."""

    def __init__(
        self, template_dir: Path | str, config: RenderConfig | None = None
    ):
        """
        Initialize Jinja2 renderer.

        Args:
            template_dir: Directory containing templates
            config: Rendering configuration
        """
        super().__init__(template_dir, config)
        self._env = self._create_environment()

    def _create_environment(self) -> Environment:
        """Create and configure Jinja2 environment."""
        env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=self.config.autoescape,
            trim_blocks=self.config.trim_blocks,
            lstrip_blocks=self.config.lstrip_blocks,
            keep_trailing_newline=self.config.keep_trailing_newline,
            undefined=StrictUndefined if self.config.strict_mode else None,
        )

        # Add custom filters, tests, and globals
        if self.config.custom_filters:
            env.filters.update(self.config.custom_filters)
        if self.config.custom_tests:
            env.tests.update(self.config.custom_tests)
        if self.config.custom_globals:
            env.globals.update(self.config.custom_globals)

        return env

    def render(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Render a template with the given variables.

        Args:
            template_name: Name of the template file
            variables: Variables to use in rendering
            **kwargs: Additional variables (merged with variables dict)

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateRenderError: If rendering fails
            MissingVariableError: If required variables are missing
                (strict mode)
        """
        # Merge variables
        all_variables = {**(variables or {}), **kwargs}

        # Validate if strict mode
        if self.config.strict_mode:
            validation = self.validate(template_name, all_variables)
            if not validation.is_valid:
                raise MissingVariableError(
                    validation.missing_variables, template_name
                )

        try:
            template = self._env.get_template(template_name)
            return template.render(**all_variables)
        except TemplateNotFound as e:
            raise TemplateNotFoundError(
                template_name,
                [str(self.template_dir)],
            ) from e
        except UndefinedError as e:
            # This shouldn't happen if validation works, but just in case
            raise MissingVariableError(
                [str(e)],
                template_name,
            ) from e
        except Exception as e:
            raise TemplateRenderError(
                f"Failed to render template: {e}",
                template_name,
                e,
            ) from e

    def validate(
        self,
        template_name: str,
        variables: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """
        Validate that all required variables are provided.

        Args:
            template_name: Name of the template file
            variables: Variables to validate against template

        Returns:
            ValidationResult with details about missing/unused variables
        """
        variables = variables or {}

        try:
            # Get template source
            template_source = self._get_template_source(template_name)

            # Extract required variables
            required_vars = extract_jinja2_variables(
                template_source, self._env
            )

            # Validate
            return validate_variables(
                template_name,
                required_vars,
                variables,
                strict=self.config.strict_mode,
            )
        except TemplateNotFound:
            return ValidationResult(
                is_valid=False,
                errors=[f"Template not found: {template_name}"],
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {e}"],
            )

    def get_template_variables(self, template_name: str) -> list[str]:
        """
        Get list of all variables used in a template.

        Args:
            template_name: Name of the template file

        Returns:
            List of variable names found in the template

        Raises:
            TemplateNotFoundError: If template doesn't exist
        """
        try:
            template_source = self._get_template_source(template_name)
            variables = extract_jinja2_variables(template_source, self._env)
            return sorted(variables)
        except TemplateNotFound as e:
            raise TemplateNotFoundError(
                template_name,
                [str(self.template_dir)],
            ) from e

    def get_available_templates(self) -> list[str]:
        """
        Get list of all available template files.

        Returns:
            List of template file names
        """
        templates = []
        for path in self.template_dir.rglob("*"):
            if path.is_file() and path.suffix in [".j2", ".jinja", ".jinja2"]:
                # Get relative path from template_dir
                rel_path = path.relative_to(self.template_dir)
                templates.append(str(rel_path))
        return sorted(templates)

    def get_template_info(self, template_name: str) -> TemplateInfo:
        """
        Get detailed information about a template.

        Args:
            template_name: Name of the template file

        Returns:
            TemplateInfo with metadata about the template

        Raises:
            TemplateNotFoundError: If template doesn't exist
        """
        template_path = self.template_dir / template_name

        if not template_path.exists():
            raise TemplateNotFoundError(
                template_name,
                [str(self.template_dir)],
            )

        # Get required variables
        required_vars = self.get_template_variables(template_name)

        # Get file size
        size = template_path.stat().st_size

        # Try to extract description from template comments
        description = self._extract_description(template_path)

        return TemplateInfo(
            name=template_name,
            path=template_path,
            size=size,
            required_variables=required_vars,
            description=description,
        )

    def _get_template_source(self, template_name: str) -> str:
        """Get template source code."""
        template_path = self.template_dir / template_name
        if not template_path.exists():
            raise TemplateNotFound(template_name)
        return template_path.read_text()

    def _extract_description(self, template_path: Path) -> str | None:
        """Extract description from template comments."""
        try:
            content = template_path.read_text()
            lines = content.split("\n")

            # Look for comment at the start
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if line.startswith("{#") and line.endswith("#}"):
                    # Extract comment content
                    return line[2:-2].strip()
                elif line and not line.startswith("{#"):
                    # Stop if we hit non-comment content
                    break

            return None
        except Exception:
            return None

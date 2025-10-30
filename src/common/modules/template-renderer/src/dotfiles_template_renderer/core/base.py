"""Abstract base class for template renderers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .types import RenderConfig, TemplateContext, TemplateInfo, ValidationResult


class TemplateRenderer(ABC):
    """Abstract base class for template rendering engines."""

    def __init__(self, template_dir: Path | str, config: RenderConfig | None = None):
        """
        Initialize the template renderer.

        Args:
            template_dir: Directory containing templates
            config: Rendering configuration
        """
        self.template_dir = Path(template_dir)
        self.config = config or RenderConfig()

        if not self.template_dir.exists():
            raise FileNotFoundError(
                f"Template directory does not exist: {self.template_dir}"
            )

    @abstractmethod
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
            MissingVariableError: If required variables are missing (strict mode)
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_available_templates(self) -> list[str]:
        """
        Get list of all available template files.

        Returns:
            List of template file names
        """
        pass

    @abstractmethod
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
        pass

    def render_from_context(self, context: TemplateContext) -> str:
        """
        Render a template using a TemplateContext object.

        Args:
            context: Template context with name, variables, and config

        Returns:
            Rendered template as string
        """
        # Temporarily override config if provided in context
        original_config = self.config
        if context.config:
            self.config = context.config

        try:
            return self.render(context.template_name, context.variables)
        finally:
            self.config = original_config

    def render_to_file(
        self,
        template_name: str,
        output_path: Path | str,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Render a template and write to a file.

        Args:
            template_name: Name of the template file
            output_path: Path where rendered content should be written
            variables: Variables to use in rendering
            **kwargs: Additional variables
        """
        rendered = self.render(template_name, variables, **kwargs)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered)


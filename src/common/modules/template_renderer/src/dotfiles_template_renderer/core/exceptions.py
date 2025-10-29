"""Exceptions for template rendering."""

from typing import Any


class TemplateError(Exception):
    """Base exception for template rendering errors."""

    def __init__(self, message: str, template_name: str | None = None):
        """
        Initialize template error.

        Args:
            message: Error message
            template_name: Name of the template that caused the error
        """
        self.message = message
        self.template_name = template_name
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message."""
        if self.template_name:
            return f"Template '{self.template_name}': {self.message}"
        return self.message


class TemplateNotFoundError(TemplateError):
    """Raised when a template file cannot be found."""

    def __init__(self, template_name: str, search_paths: list[str] | None = None):
        """
        Initialize template not found error.

        Args:
            template_name: Name of the template that was not found
            search_paths: Paths that were searched
        """
        self.search_paths = search_paths or []
        message = f"Template not found: {template_name}"
        if search_paths:
            message += f"\nSearched in: {', '.join(search_paths)}"
        super().__init__(message, template_name)


class TemplateRenderError(TemplateError):
    """Raised when template rendering fails."""

    def __init__(
        self,
        message: str,
        template_name: str | None = None,
        original_error: Exception | None = None,
    ):
        """
        Initialize template render error.

        Args:
            message: Error message
            template_name: Name of the template
            original_error: Original exception that caused the error
        """
        self.original_error = original_error
        super().__init__(message, template_name)


class ValidationError(TemplateError):
    """Raised when template validation fails."""

    pass


class MissingVariableError(ValidationError):
    """Raised when required template variables are missing."""

    def __init__(
        self,
        missing_variables: list[str],
        template_name: str | None = None,
    ):
        """
        Initialize missing variable error.

        Args:
            missing_variables: List of missing variable names
            template_name: Name of the template
        """
        self.missing_variables = missing_variables
        message = f"Missing required variables: {', '.join(missing_variables)}"
        super().__init__(message, template_name)


class InvalidVariableError(ValidationError):
    """Raised when a variable has an invalid value."""

    def __init__(
        self,
        variable_name: str,
        value: Any,
        reason: str,
        template_name: str | None = None,
    ):
        """
        Initialize invalid variable error.

        Args:
            variable_name: Name of the invalid variable
            value: The invalid value
            reason: Reason why the value is invalid
            template_name: Name of the template
        """
        self.variable_name = variable_name
        self.value = value
        self.reason = reason
        message = f"Invalid value for variable '{variable_name}': {reason}"
        super().__init__(message, template_name)


"""Tests for error handling and exceptions."""

import pytest

from dotfiles_template_renderer import (
    InvalidVariableError,
    MissingVariableError,
    TemplateError,
    TemplateNotFoundError,
    TemplateRenderError,
    ValidationError,
)


class TestTemplateError:
    """Tests for base TemplateError exception."""

    def test_template_error_can_be_raised(self):
        """Test that TemplateError can be raised."""
        with pytest.raises(TemplateError):
            raise TemplateError("Test error")

    def test_template_error_message(self):
        """Test TemplateError message."""
        error = TemplateError("Test error message")
        assert str(error) == "Test error message"

    def test_template_error_is_exception(self):
        """Test that TemplateError is an Exception."""
        error = TemplateError("Test")
        assert isinstance(error, Exception)


class TestTemplateNotFoundError:
    """Tests for TemplateNotFoundError exception."""

    def test_template_not_found_error_basic(self):
        """Test basic TemplateNotFoundError."""
        with pytest.raises(TemplateNotFoundError):
            raise TemplateNotFoundError("template.j2")

    def test_template_not_found_error_with_search_paths(self):
        """Test TemplateNotFoundError with search paths."""
        search_paths = ["/path1", "/path2"]
        error = TemplateNotFoundError("template.j2", search_paths)

        assert error.template_name == "template.j2"
        assert error.search_paths == search_paths
        assert "template.j2" in str(error)

    def test_template_not_found_error_without_search_paths(self):
        """Test TemplateNotFoundError without search paths."""
        error = TemplateNotFoundError("template.j2")

        assert error.template_name == "template.j2"
        assert error.search_paths == []

    def test_template_not_found_error_is_template_error(self):
        """Test that TemplateNotFoundError is a TemplateError."""
        error = TemplateNotFoundError("template.j2")
        assert isinstance(error, TemplateError)

    def test_template_not_found_error_message_format(self):
        """Test TemplateNotFoundError message format."""
        error = TemplateNotFoundError("missing.j2", ["/templates"])
        message = str(error)

        assert "missing.j2" in message
        assert "not found" in message.lower()


class TestTemplateRenderError:
    """Tests for TemplateRenderError exception."""

    def test_template_render_error_basic(self):
        """Test basic TemplateRenderError."""
        with pytest.raises(TemplateRenderError):
            raise TemplateRenderError("Render failed", "template.j2")

    def test_template_render_error_with_details(self):
        """Test TemplateRenderError with details."""
        error = TemplateRenderError(
            "Syntax error",
            "template.j2",
            original_error=ValueError("Invalid syntax"),
        )

        assert error.template_name == "template.j2"
        assert "template.j2" in str(error)
        assert "Syntax error" in str(error)

    def test_template_render_error_is_template_error(self):
        """Test that TemplateRenderError is a TemplateError."""
        error = TemplateRenderError("Error", "template.j2")
        assert isinstance(error, TemplateError)

    def test_template_render_error_preserves_original_error(self):
        """Test that TemplateRenderError preserves original error."""
        original = ValueError("Original error")
        error = TemplateRenderError(
            "Render failed", "template.j2", original_error=original
        )

        assert error.original_error is original


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_basic(self):
        """Test basic ValidationError."""
        with pytest.raises(ValidationError):
            raise ValidationError("Validation failed")

    def test_validation_error_with_template_name(self):
        """Test ValidationError with template name."""
        error = ValidationError("Validation failed", template_name="test.j2")

        assert error.template_name == "test.j2"
        assert "test.j2" in str(error)

    def test_validation_error_is_template_error(self):
        """Test that ValidationError is a TemplateError."""
        error = ValidationError("Validation failed")
        assert isinstance(error, TemplateError)


class TestMissingVariableError:
    """Tests for MissingVariableError exception."""

    def test_missing_variable_error_single_variable(self):
        """Test MissingVariableError with single variable."""
        with pytest.raises(MissingVariableError):
            raise MissingVariableError(["name"], "template.j2")

    def test_missing_variable_error_multiple_variables(self):
        """Test MissingVariableError with multiple variables."""
        error = MissingVariableError(["name", "age", "email"], "template.j2")

        assert error.template_name == "template.j2"
        assert error.missing_variables == ["name", "age", "email"]
        assert "name" in str(error)
        assert "age" in str(error)
        assert "email" in str(error)

    def test_missing_variable_error_is_validation_error(self):
        """Test that MissingVariableError is a ValidationError."""
        error = MissingVariableError(["name"], "template.j2")
        assert isinstance(error, ValidationError)

    def test_missing_variable_error_message_format(self):
        """Test MissingVariableError message format."""
        error = MissingVariableError(["var1", "var2"], "test.j2")
        message = str(error)

        assert "test.j2" in message
        assert "missing" in message.lower()
        assert "var1" in message
        assert "var2" in message


class TestInvalidVariableError:
    """Tests for InvalidVariableError exception."""

    def test_invalid_variable_error_basic(self):
        """Test basic InvalidVariableError."""
        with pytest.raises(InvalidVariableError):
            raise InvalidVariableError(
                "name", "bad_value", "Invalid value", "template.j2"
            )

    def test_invalid_variable_error_with_details(self):
        """Test InvalidVariableError with details."""
        error = InvalidVariableError(
            "age",
            "30",
            "Expected int, got str",
            "template.j2",
        )

        assert error.template_name == "template.j2"
        assert error.variable_name == "age"
        assert "age" in str(error)

    def test_invalid_variable_error_is_validation_error(self):
        """Test that InvalidVariableError is a ValidationError."""
        error = InvalidVariableError("name", "value", "Invalid", "template.j2")
        assert isinstance(error, ValidationError)


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_exceptions_inherit_from_template_error(self):
        """Test that all exceptions inherit from TemplateError."""
        exceptions = [
            TemplateNotFoundError("test.j2"),
            TemplateRenderError("Error", "test.j2"),
            ValidationError("Error"),
            MissingVariableError(["var"], "test.j2"),
            InvalidVariableError("var", "value", "Error", "test.j2"),
        ]

        for exc in exceptions:
            assert isinstance(exc, TemplateError)

    def test_validation_errors_inherit_from_validation_error(self):
        """Test that validation errors inherit from ValidationError."""
        exceptions = [
            MissingVariableError(["var"], "test.j2"),
            InvalidVariableError("var", "value", "Error", "test.j2"),
        ]

        for exc in exceptions:
            assert isinstance(exc, ValidationError)

    def test_can_catch_all_with_template_error(self):
        """Test that all exceptions can be caught with TemplateError."""
        exceptions = [
            TemplateNotFoundError("test.j2"),
            TemplateRenderError("Error", "test.j2"),
            MissingVariableError(["var"], "test.j2"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except TemplateError:
                pass  # Successfully caught
            else:
                pytest.fail(f"Failed to catch {type(exc).__name__}")

    def test_can_catch_validation_errors_specifically(self):
        """Test that validation errors can be caught specifically."""
        exceptions = [
            MissingVariableError(["var"], "test.j2"),
            InvalidVariableError("var", "value", "Error", "test.j2"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except ValidationError:
                pass  # Successfully caught
            else:
                pytest.fail(f"Failed to catch {type(exc).__name__}")


class TestExceptionAttributes:
    """Tests for exception attributes."""

    def test_template_not_found_error_attributes(self):
        """Test TemplateNotFoundError attributes."""
        error = TemplateNotFoundError("test.j2", ["/path1", "/path2"])

        assert hasattr(error, "template_name")
        assert hasattr(error, "search_paths")
        assert error.template_name == "test.j2"
        assert len(error.search_paths) == 2

    def test_template_render_error_attributes(self):
        """Test TemplateRenderError attributes."""
        original = ValueError("Original")
        error = TemplateRenderError(
            "Error", "test.j2", original_error=original
        )

        assert hasattr(error, "template_name")
        assert hasattr(error, "original_error")
        assert error.template_name == "test.j2"
        assert error.original_error is original

    def test_missing_variable_error_attributes(self):
        """Test MissingVariableError attributes."""
        error = MissingVariableError(["var1", "var2"], "test.j2")

        assert hasattr(error, "template_name")
        assert hasattr(error, "missing_variables")
        assert error.template_name == "test.j2"
        assert error.missing_variables == ["var1", "var2"]

    def test_invalid_variable_error_attributes(self):
        """Test InvalidVariableError attributes."""
        error = InvalidVariableError(
            "age",
            "30",
            "Type error",
            "test.j2",
        )

        assert hasattr(error, "template_name")
        assert hasattr(error, "variable_name")
        assert hasattr(error, "value")
        assert hasattr(error, "reason")
        assert error.template_name == "test.j2"
        assert error.variable_name == "age"
        assert error.value == "30"
        assert error.reason == "Type error"

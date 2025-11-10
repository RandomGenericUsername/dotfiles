"""Tests for template validation utilities."""

from jinja2 import Environment

from dotfiles_template_renderer import (
    extract_jinja2_variables,
    validate_variable_types,
    validate_variables,
)


class TestExtractJinja2Variables:
    """Tests for extracting variables from Jinja2 templates."""

    def test_extract_single_variable(self):
        """Test extracting a single variable."""
        template = "Hello {{ name }}!"
        env = Environment()

        variables = extract_jinja2_variables(template, env)
        assert "name" in variables

    def test_extract_multiple_variables(self):
        """Test extracting multiple variables."""
        template = "{{ greeting }} {{ name }}, you are {{ age }} years old"
        env = Environment()

        variables = extract_jinja2_variables(template, env)
        assert "greeting" in variables
        assert "name" in variables
        assert "age" in variables

    def test_extract_variables_with_filters(self):
        """Test extracting variables that use filters."""
        template = "{{ name | upper }} - {{ date | format_date }}"
        env = Environment()

        variables = extract_jinja2_variables(template, env)
        assert "name" in variables
        assert "date" in variables

    def test_extract_variables_in_loops(self):
        """Test extracting variables used in loops."""
        template = """
        {% for item in items %}
            {{ item.name }}
        {% endfor %}
        """
        env = Environment()

        variables = extract_jinja2_variables(template, env)
        assert "items" in variables

    def test_extract_variables_in_conditionals(self):
        """Test extracting variables used in conditionals."""
        template = """
        {% if condition %}
            {{ value }}
        {% endif %}
        """
        env = Environment()

        variables = extract_jinja2_variables(template, env)
        assert "condition" in variables
        assert "value" in variables

    def test_extract_variables_with_attributes(self):
        """Test extracting variables with attribute access."""
        template = "{{ user.name }} - {{ user.email }}"
        env = Environment()

        variables = extract_jinja2_variables(template, env)
        assert "user" in variables

    def test_extract_no_variables(self):
        """Test extracting from template with no variables."""
        template = "This is static content"
        env = Environment()

        variables = extract_jinja2_variables(template, env)
        assert len(variables) == 0

    def test_extract_variables_with_defaults(self):
        """Test extracting variables with default values."""
        template = "{{ name | default('Guest') }}"
        env = Environment()

        variables = extract_jinja2_variables(template, env)
        assert "name" in variables


class TestValidateVariables:
    """Tests for variable validation."""

    def test_validate_all_variables_provided(self):
        """Test validation when all variables are provided."""
        required = {"name", "age"}
        provided = {"name": "Alice", "age": 30}

        result = validate_variables("test.j2", required, provided, strict=True)
        assert result.is_valid
        assert len(result.missing_variables) == 0
        assert len(result.errors) == 0

    def test_validate_missing_variables_strict(self):
        """Test validation with missing variables in strict mode."""
        required = {"name", "age", "email"}
        provided = {"name": "Alice"}

        result = validate_variables("test.j2", required, provided, strict=True)
        assert not result.is_valid
        assert "age" in result.missing_variables
        assert "email" in result.missing_variables
        assert len(result.errors) > 0

    def test_validate_missing_variables_non_strict(self):
        """Test validation with missing variables in non-strict mode."""
        required = {"name", "age"}
        provided = {"name": "Alice"}

        result = validate_variables(
            "test.j2", required, provided, strict=False
        )
        assert result.is_valid  # Non-strict mode is still valid
        assert "age" in result.missing_variables
        assert len(result.warnings) > 0
        assert len(result.errors) == 0

    def test_validate_unused_variables(self):
        """Test validation detects unused variables."""
        required = {"name"}
        provided = {"name": "Alice", "unused1": "value", "unused2": 123}

        result = validate_variables("test.j2", required, provided, strict=True)
        assert result.is_valid
        assert "unused1" in result.unused_variables
        assert "unused2" in result.unused_variables
        assert len(result.warnings) > 0

    def test_validate_no_variables_required(self):
        """Test validation when no variables are required."""
        required = set()
        provided = {}

        result = validate_variables("test.j2", required, provided, strict=True)
        assert result.is_valid
        assert len(result.missing_variables) == 0

    def test_validate_extra_variables_only(self):
        """Test validation with only extra variables."""
        required = set()
        provided = {"extra1": "value", "extra2": 123}

        result = validate_variables("test.j2", required, provided, strict=True)
        assert result.is_valid
        assert "extra1" in result.unused_variables
        assert "extra2" in result.unused_variables

    def test_validate_required_variables_list(self):
        """Test that required_variables is populated."""
        required = {"name", "age", "email"}
        provided = {"name": "Alice", "age": 30, "email": "alice@example.com"}

        result = validate_variables("test.j2", required, provided, strict=True)
        assert len(result.required_variables) == 3
        assert "name" in result.required_variables
        assert "age" in result.required_variables
        assert "email" in result.required_variables


class TestValidateVariableTypes:
    """Tests for variable type validation."""

    def test_validate_correct_types(self):
        """Test validation with correct types."""
        variables = {"name": "Alice", "age": 30, "active": True}
        expected_types = {"name": str, "age": int, "active": bool}

        errors = validate_variable_types(variables, expected_types)
        assert len(errors) == 0

    def test_validate_incorrect_type(self):
        """Test validation with incorrect type."""
        variables = {"name": "Alice", "age": "30"}  # age should be int
        expected_types = {"name": str, "age": int}

        errors = validate_variable_types(variables, expected_types)
        assert len(errors) == 1
        assert "age" in errors[0]
        assert "str" in errors[0]
        assert "int" in errors[0]

    def test_validate_multiple_incorrect_types(self):
        """Test validation with multiple incorrect types."""
        variables = {"name": 123, "age": "30", "active": "yes"}
        expected_types = {"name": str, "age": int, "active": bool}

        errors = validate_variable_types(variables, expected_types)
        assert len(errors) == 3

    def test_validate_missing_variable_not_error(self):
        """Test that missing variables don't cause type errors."""
        variables = {"name": "Alice"}
        expected_types = {"name": str, "age": int}

        errors = validate_variable_types(variables, expected_types)
        assert len(errors) == 0  # Missing variables are not type errors

    def test_validate_no_expected_types(self):
        """Test validation with no expected types."""
        variables = {"name": "Alice", "age": 30}

        errors = validate_variable_types(variables, None)
        assert len(errors) == 0

    def test_validate_empty_expected_types(self):
        """Test validation with empty expected types dict."""
        variables = {"name": "Alice", "age": 30}
        expected_types = {}

        errors = validate_variable_types(variables, expected_types)
        assert len(errors) == 0

    def test_validate_complex_types(self):
        """Test validation with complex types."""
        variables = {
            "items": ["a", "b", "c"],
            "config": {"key": "value"},
            "count": 42,
        }
        expected_types = {
            "items": list,
            "config": dict,
            "count": int,
        }

        errors = validate_variable_types(variables, expected_types)
        assert len(errors) == 0

    def test_validate_none_value(self):
        """Test validation with None value."""
        variables = {"name": None}
        expected_types = {"name": str}

        errors = validate_variable_types(variables, expected_types)
        assert len(errors) == 1
        assert "name" in errors[0]


class TestValidationIntegration:
    """Integration tests for validation functions."""

    def test_full_validation_workflow(self):
        """Test complete validation workflow."""
        # Extract variables from template
        template = "Hello {{ name }}, you are {{ age }} years old"
        env = Environment()
        required_vars = extract_jinja2_variables(template, env)

        # Validate with correct variables
        provided = {"name": "Alice", "age": 30}
        result = validate_variables(
            "test.j2", required_vars, provided, strict=True
        )
        assert result.is_valid

        # Validate types
        expected_types = {"name": str, "age": int}
        type_errors = validate_variable_types(provided, expected_types)
        assert len(type_errors) == 0

    def test_validation_with_missing_and_wrong_types(self):
        """Test validation with both missing variables and wrong types."""
        template = "{{ name }} - {{ age }} - {{ email }}"
        env = Environment()
        required_vars = extract_jinja2_variables(template, env)

        # Missing 'email', wrong type for 'age'
        provided = {"name": "Alice", "age": "30"}

        # Check missing variables
        result = validate_variables(
            "test.j2", required_vars, provided, strict=True
        )
        assert not result.is_valid
        assert "email" in result.missing_variables

        # Check type errors
        expected_types = {"name": str, "age": int, "email": str}
        type_errors = validate_variable_types(provided, expected_types)
        assert len(type_errors) == 1
        assert "age" in type_errors[0]

"""Template validation utilities."""

import re
from typing import Any

from jinja2 import Environment, meta

from .core.types import ValidationResult


def extract_jinja2_variables(template_source: str, env: Environment) -> set[str]:
    """
    Extract all variables from a Jinja2 template.

    Args:
        template_source: Template source code
        env: Jinja2 environment

    Returns:
        Set of variable names found in the template
    """
    try:
        ast = env.parse(template_source)
        return meta.find_undeclared_variables(ast)
    except Exception:
        # Fallback to regex if parsing fails
        return extract_variables_regex(template_source)


def extract_variables_regex(template_source: str) -> set[str]:
    """
    Extract variables using regex (fallback method).

    Args:
        template_source: Template source code

    Returns:
        Set of variable names found in the template
    """
    # Match {{ variable }}, {{ variable.attr }}, {{ variable['key'] }}
    pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)"
    matches = re.findall(pattern, template_source)
    return set(matches)


def validate_variables(
    template_name: str,
    required_variables: set[str],
    provided_variables: dict[str, Any],
    strict: bool = True,
) -> ValidationResult:
    """
    Validate that all required variables are provided.

    Args:
        template_name: Name of the template
        required_variables: Variables required by the template
        provided_variables: Variables provided for rendering
        strict: Whether to fail on missing variables

    Returns:
        ValidationResult with validation details
    """
    provided_keys = set(provided_variables.keys())
    missing = required_variables - provided_keys
    unused = provided_keys - required_variables

    errors = []
    warnings = []

    if missing:
        if strict:
            errors.append(
                f"Missing required variables: {', '.join(sorted(missing))}"
            )
        else:
            warnings.append(
                f"Missing variables (will use defaults): {', '.join(sorted(missing))}"
            )

    if unused:
        warnings.append(
            f"Unused variables provided: {', '.join(sorted(unused))}"
        )

    is_valid = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        missing_variables=sorted(missing),
        unused_variables=sorted(unused),
        required_variables=sorted(required_variables),
        errors=errors,
        warnings=warnings,
    )


def validate_variable_types(
    variables: dict[str, Any],
    expected_types: dict[str, type] | None = None,
) -> list[str]:
    """
    Validate variable types.

    Args:
        variables: Variables to validate
        expected_types: Expected types for each variable

    Returns:
        List of validation error messages
    """
    if not expected_types:
        return []

    errors = []
    for var_name, expected_type in expected_types.items():
        if var_name in variables:
            value = variables[var_name]
            if not isinstance(value, expected_type):
                errors.append(
                    f"Variable '{var_name}' has type {type(value).__name__}, "
                    f"expected {expected_type.__name__}"
                )

    return errors


# Investigation Notes - Detailed Findings

**Investigation Target:** `template_renderer` module
**Created:** 2025-10-18
**Last Updated:** 2025-10-18

---

## Table of Contents

1. [Architecture & Structure](#architecture--structure)
2. [Core Abstractions](#core-abstractions)
3. [Type System & Data Models](#type-system--data-models)
4. [Exception Hierarchy](#exception-hierarchy)
5. [Implementation Details](#implementation-details)
6. [Key Features & Capabilities](#key-features--capabilities)
7. [Integration & Usage Patterns](#integration--usage-patterns)
8. [Advanced Topics](#advanced-topics)
9. [Code Examples](#code-examples)
10. [Architecture Diagrams](#architecture-diagrams)

---

## Architecture & Structure

### Directory Structure

```
template_renderer/
├── __init__.py
├── README.md
├── validators.py
├── core/
│   ├── __init__.py
│   ├── base.py
│   ├── exceptions.py
│   └── types.py
└── renderers/
    ├── __init__.py
    └── jinja2.py
```

### File Purposes

**Root Level:**
- `__init__.py` - Public API exports (all core types, renderers, validators, exceptions)
- `README.md` - User-facing documentation with examples and usage patterns
- `validators.py` - Template validation utilities (variable extraction, validation)

**core/ Directory:**
- `__init__.py` - Core component exports (base classes, exceptions, types)
- `base.py` - Abstract base class `TemplateRenderer` defining the renderer contract
- `exceptions.py` - Complete exception hierarchy for template errors
- `types.py` - Data models (RenderConfig, TemplateContext, ValidationResult, TemplateInfo)

**renderers/ Directory:**
- `__init__.py` - Renderer implementation exports
- `jinja2.py` - Concrete Jinja2 implementation of TemplateRenderer

### Module Organization

The module follows a **layered architecture**:

1. **Core Layer** (`core/`): Abstract interfaces and contracts
   - Base classes defining the renderer contract
   - Type definitions for configuration and results
   - Exception hierarchy for error handling

2. **Implementation Layer** (`renderers/`): Concrete implementations
   - Jinja2Renderer - production-ready Jinja2 implementation
   - Extensible design allows adding more renderers (Mako, Mustache, etc.)

3. **Utility Layer** (root): Shared utilities
   - validators.py - Variable extraction and validation logic
   - Agnostic to specific renderer implementation

4. **Public API** (`__init__.py`): Clean, organized exports
   - Grouped by category (Core, Renderers, Exceptions, Validators)
   - Single import point for consumers

### Public API Surface

**Classes:**
- `TemplateRenderer` - Abstract base class for all renderers
- `Jinja2Renderer` - Jinja2 implementation
- `RenderConfig` - Configuration dataclass
- `TemplateContext` - Context dataclass for rendering
- `TemplateInfo` - Template metadata dataclass
- `ValidationResult` - Validation result dataclass

**Exceptions:**
- `TemplateError` - Base exception
- `TemplateNotFoundError` - Template file not found
- `TemplateRenderError` - Rendering failed
- `ValidationError` - Validation failed
- `MissingVariableError` - Required variables missing
- `InvalidVariableError` - Invalid variable value

**Functions:**
- `extract_jinja2_variables(template_source, env)` - Extract variables from template
- `validate_variables(template_name, required_vars, provided_vars, strict)` - Validate variables
- `validate_variable_types(variables, expected_types)` - Validate variable types

### Entry Points

**Primary Entry Point:**
```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig
```

**Common Usage Patterns:**
1. Direct instantiation: `renderer = Jinja2Renderer(template_dir, config)`
2. Pipeline integration: `RenderTemplateStep` in pipeline_steps.container_steps
3. Standalone validation: Import validators directly for pre-validation

**Integration Points:**
- Used by `pipeline_steps.container_steps.RenderTemplateStep` for pipeline integration
- Can be used standalone for any template rendering needs
- Designed to be framework-agnostic

---

## Core Abstractions

### Abstract Base Classes

**TemplateRenderer (core/base.py)**

The central abstraction defining the contract for all template renderers.

**Purpose:** Provide a consistent interface for template rendering regardless of the underlying engine

**Design Philosophy:**
- Engine-agnostic: Works with any template engine (Jinja2, Mako, Mustache, etc.)
- Validation-first: Built-in validation before rendering
- Introspection: Ability to query template requirements
- Flexible configuration: Customizable rendering behavior

**Abstract Methods (Must Implement):**
1. `render(template_name, variables, **kwargs) -> str`
   - Core rendering method
   - Must handle variable merging
   - Must raise appropriate exceptions

2. `validate(template_name, variables) -> ValidationResult`
   - Validate variables against template requirements
   - Return detailed validation results

3. `get_template_variables(template_name) -> list[str]`
   - Extract all variables from template
   - Used for introspection and validation

4. `get_available_templates() -> list[str]`
   - List all templates in template directory
   - Used for discovery and validation

5. `get_template_info(template_name) -> TemplateInfo`
   - Get detailed metadata about a template
   - Includes size, variables, description

**Concrete Methods (Provided):**
1. `render_from_context(context: TemplateContext) -> str`
   - Convenience method using TemplateContext object
   - Temporarily overrides config if provided in context
   - Ensures config is restored after rendering

2. `render_to_file(template_name, output_path, variables, **kwargs) -> None`
   - Render and write to file in one operation
   - Creates parent directories automatically
   - Useful for generating configuration files

**Constructor Contract:**
- Must accept `template_dir: Path | str`
- Must accept optional `config: RenderConfig | None`
- Must validate template_dir exists
- Must raise FileNotFoundError if directory doesn't exist

### Interfaces/Protocols

**No explicit Protocol classes**, but implicit contracts:

1. **Renderer Contract** (via TemplateRenderer ABC)
   - All renderers must implement the 5 abstract methods
   - All renderers must handle the same exception types
   - All renderers must use the same type definitions

2. **Configuration Contract** (via RenderConfig)
   - All renderers must respect RenderConfig settings
   - strict_mode must control validation behavior
   - Custom filters/tests/globals must be supported

3. **Validation Contract** (via ValidationResult)
   - Validation must return consistent ValidationResult structure
   - Must track missing, unused, and required variables
   - Must provide errors and warnings lists

### Core Concepts

**1. Template Agnosticism**
- Module doesn't care what it's rendering (Dockerfiles, configs, scripts, etc.)
- Separation of concerns: rendering logic vs. content semantics
- Reusable across different use cases

**2. Strict vs. Lenient Modes**
- **Strict Mode** (default): Fail fast on missing variables
- **Lenient Mode**: Allow missing variables, use defaults
- Controlled via `RenderConfig.strict_mode`

**3. Variable Validation**
- Pre-rendering validation to catch errors early
- Separate validation step from rendering step
- Detailed feedback on missing/unused variables

**4. Template Introspection**
- Discover template requirements without rendering
- Query available templates
- Get metadata about templates

**5. Configuration Flexibility**
- Per-renderer configuration via RenderConfig
- Custom filters, tests, and globals
- Jinja2-specific settings (autoescape, trim_blocks, etc.)

**6. Context-Based Rendering**
- TemplateContext encapsulates all rendering parameters
- Allows passing rendering jobs as objects
- Supports temporary config overrides

### Inheritance Hierarchies

**Renderer Hierarchy:**
```
ABC (Python built-in)
  └── TemplateRenderer (abstract)
        └── Jinja2Renderer (concrete)
```

**Exception Hierarchy:**
```
Exception (Python built-in)
  └── TemplateError (base)
        ├── TemplateNotFoundError
        ├── TemplateRenderError
        └── ValidationError
              ├── MissingVariableError
              └── InvalidVariableError
```

**Type Hierarchy:**
- All types are dataclasses (no inheritance)
- RenderConfig, TemplateContext, ValidationResult, TemplateInfo are independent

### Design Contracts

**Contract 1: Renderer Initialization**
- MUST validate template_dir exists
- MUST raise FileNotFoundError if directory missing
- MUST store template_dir as Path object
- MUST create default RenderConfig if none provided

**Contract 2: Rendering**
- MUST merge variables dict with kwargs
- MUST validate in strict mode before rendering
- MUST raise MissingVariableError if validation fails in strict mode
- MUST raise TemplateNotFoundError if template doesn't exist
- MUST raise TemplateRenderError for other rendering failures
- MUST return rendered string

**Contract 3: Validation**
- MUST return ValidationResult object
- MUST populate missing_variables list
- MUST populate unused_variables list
- MUST populate required_variables list
- MUST set is_valid based on errors
- MUST handle template not found gracefully (return invalid result)

**Contract 4: Variable Extraction**
- MUST return list of all variables in template
- MUST raise TemplateNotFoundError if template doesn't exist
- MUST return sorted list for consistency

**Contract 5: Template Discovery**
- MUST return list of all available templates
- MUST return relative paths from template_dir
- MUST return sorted list for consistency

**Contract 6: Template Info**
- MUST return TemplateInfo object
- MUST raise TemplateNotFoundError if template doesn't exist
- MUST include name, path, size, required_variables
- MAY include description (optional)

---

## Type System & Data Models

### Enums

**No enums defined in this module.**

The module uses string literals for configuration options (e.g., `undefined_behavior: str = "strict"`).

**Potential Future Enums:**
- UndefinedBehavior: Enum["strict", "default", "debug"]
- TemplateFormat: Enum[".j2", ".jinja", ".jinja2"]

### Dataclasses/Models

**1. RenderConfig (core/types.py)**

Configuration for template rendering behavior.

```python
@dataclass
class RenderConfig:
    strict_mode: bool = True
    autoescape: bool = False
    trim_blocks: bool = True
    lstrip_blocks: bool = True
    keep_trailing_newline: bool = True
    undefined_behavior: str = "strict"
    custom_filters: dict[str, Any] = field(default_factory=dict)
    custom_tests: dict[str, Any] = field(default_factory=dict)
    custom_globals: dict[str, Any] = field(default_factory=dict)
```

**Fields:**
- `strict_mode`: Fail if required variables are missing (default: True)
- `autoescape`: Enable autoescaping for HTML/XML templates (default: False)
- `trim_blocks`: Remove first newline after template tag (default: True)
- `lstrip_blocks`: Strip leading spaces/tabs from start of line to block (default: True)
- `keep_trailing_newline`: Keep trailing newline at end of template (default: True)
- `undefined_behavior`: How to handle undefined variables (default: "strict")
- `custom_filters`: Custom Jinja2 filters to add (default: {})
- `custom_tests`: Custom Jinja2 tests to add (default: {})
- `custom_globals`: Custom global variables/functions (default: {})

**Usage:** Configure renderer behavior, passed to TemplateRenderer constructor

**2. TemplateContext (core/types.py)**

Context for template rendering operations.

```python
@dataclass
class TemplateContext:
    template_name: str
    variables: dict[str, Any]
    config: RenderConfig = field(default_factory=RenderConfig)
```

**Fields:**
- `template_name`: Name of the template file
- `variables`: Variables to use in template rendering
- `config`: Rendering configuration (default: new RenderConfig())

**Usage:** Encapsulate rendering parameters, used with `render_from_context()`

**3. ValidationResult (core/types.py)**

Result of template validation.

```python
@dataclass
class ValidationResult:
    is_valid: bool
    missing_variables: list[str] = field(default_factory=list)
    unused_variables: list[str] = field(default_factory=list)
    required_variables: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
```

**Fields:**
- `is_valid`: Whether the template is valid
- `missing_variables`: Variables required by template but not provided
- `unused_variables`: Variables provided but not used in template
- `required_variables`: All variables required by the template
- `errors`: Validation error messages
- `warnings`: Validation warning messages

**Usage:** Return value from `validate()` method, provides detailed validation feedback

**4. TemplateInfo (core/types.py)**

Information about a template.

```python
@dataclass
class TemplateInfo:
    name: str
    path: Path
    size: int
    required_variables: list[str] = field(default_factory=list)
    optional_variables: list[str] = field(default_factory=list)
    description: str | None = None
```

**Fields:**
- `name`: Template name
- `path`: Full path to template file
- `size`: File size in bytes
- `required_variables`: Variables required by this template
- `optional_variables`: Variables with default values (currently unused)
- `description`: Template description from docstring or metadata (optional)

**Usage:** Return value from `get_template_info()`, provides template metadata

### Type Relationships

```
RenderConfig ──> TemplateRenderer (constructor parameter)
                       │
                       ├──> render() ──> str
                       │
                       ├──> validate() ──> ValidationResult
                       │
                       ├──> get_template_info() ──> TemplateInfo
                       │
                       └──> render_from_context(TemplateContext) ──> str

TemplateContext ──> contains RenderConfig
                ──> used by render_from_context()
```

**Dependencies:**
- TemplateContext depends on RenderConfig
- ValidationResult is independent
- TemplateInfo is independent
- All types use standard Python types (str, bool, int, dict, list, Path)

### Validation Logic

**Variable Validation (validators.py):**

1. **extract_jinja2_variables(template_source, env)**
   - Uses Jinja2's AST parser to find undeclared variables
   - Fallback to regex if parsing fails
   - Returns set of variable names

2. **extract_variables_regex(template_source)**
   - Regex pattern: `r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)"`
   - Matches `{{ variable }}`, `{{ variable.attr }}`, etc.
   - Fallback method when AST parsing fails

3. **validate_variables(template_name, required_vars, provided_vars, strict)**
   - Compares required vs. provided variables
   - Identifies missing variables (required - provided)
   - Identifies unused variables (provided - required)
   - Generates errors in strict mode, warnings in lenient mode
   - Returns ValidationResult

4. **validate_variable_types(variables, expected_types)**
   - Optional type validation
   - Checks isinstance() for each variable
   - Returns list of error messages
   - Currently not used by Jinja2Renderer (could be added)

**Validation Flow:**
```
Template Source
    ↓
extract_jinja2_variables() → set of required variables
    ↓
validate_variables() → ValidationResult
    ↓
Check is_valid
    ↓
Render or Raise MissingVariableError
```

### Default Values

**RenderConfig Defaults:**
- `strict_mode = True` (fail on missing variables)
- `autoescape = False` (no HTML escaping)
- `trim_blocks = True` (clean formatting)
- `lstrip_blocks = True` (clean formatting)
- `keep_trailing_newline = True` (preserve file endings)
- `undefined_behavior = "strict"` (fail on undefined)
- `custom_filters = {}` (no custom filters)
- `custom_tests = {}` (no custom tests)
- `custom_globals = {}` (no custom globals)

**TemplateContext Defaults:**
- `config = RenderConfig()` (default config)

**ValidationResult Defaults:**
- All lists default to empty `[]`
- `description = None` in TemplateInfo

**Design Rationale:**
- Strict by default (fail fast, catch errors early)
- Clean formatting by default (trim_blocks, lstrip_blocks)
- No custom extensions by default (explicit is better than implicit)

### Type Diagrams

**Data Flow Diagram:**
```
┌─────────────────┐
│  User Code      │
└────────┬────────┘
         │
         ├─── RenderConfig ───┐
         │                    │
         ├─── template_name   │
         │                    │
         └─── variables       │
                              ↓
                    ┌──────────────────┐
                    │ TemplateRenderer │
                    └────────┬─────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ↓                 ↓
            ┌──────────────┐  ┌──────────────┐
            │  validate()  │  │   render()   │
            └──────┬───────┘  └──────┬───────┘
                   │                 │
                   ↓                 ↓
         ┌──────────────────┐  ┌─────────┐
         │ ValidationResult │  │  string │
         └──────────────────┘  └─────────┘
```

**Type Dependency Diagram:**
```
TemplateRenderer (ABC)
    ├── uses: RenderConfig
    ├── uses: TemplateContext
    ├── returns: ValidationResult
    ├── returns: TemplateInfo
    └── returns: str

Jinja2Renderer (concrete)
    ├── extends: TemplateRenderer
    ├── uses: jinja2.Environment
    └── uses: validators module
```

---

## Exception Hierarchy

### Exception Classes

**Complete Exception Hierarchy:**

```
Exception (Python built-in)
  └── TemplateError
        ├── TemplateNotFoundError
        ├── TemplateRenderError
        └── ValidationError
              ├── MissingVariableError
              └── InvalidVariableError
```

**1. TemplateError (Base Exception)**

```python
class TemplateError(Exception):
    def __init__(self, message: str, template_name: str | None = None)
```

**Attributes:**
- `message`: Error message
- `template_name`: Name of the template that caused the error (optional)

**Behavior:**
- Formats message with template name if provided
- Format: `"Template '{template_name}': {message}"`
- Base class for all template-related errors

**When Raised:** Never raised directly, only subclasses are raised

**2. TemplateNotFoundError**

```python
class TemplateNotFoundError(TemplateError):
    def __init__(self, template_name: str, search_paths: list[str] | None = None)
```

**Attributes:**
- `template_name`: Name of the template that was not found
- `search_paths`: Paths that were searched (optional)

**Behavior:**
- Includes search paths in error message if provided
- Format: `"Template not found: {template_name}\nSearched in: {paths}"`

**When Raised:**
- Template file doesn't exist in template_dir
- Called from `render()`, `validate()`, `get_template_variables()`, `get_template_info()`

**3. TemplateRenderError**

```python
class TemplateRenderError(TemplateError):
    def __init__(self, message: str, template_name: str | None = None,
                 original_error: Exception | None = None)
```

**Attributes:**
- `message`: Error message
- `template_name`: Name of the template (optional)
- `original_error`: Original exception that caused the error (optional)

**Behavior:**
- Wraps underlying rendering errors
- Preserves original exception for debugging
- Raised with `from e` to maintain exception chain

**When Raised:**
- Jinja2 rendering fails (syntax errors, runtime errors)
- Any unexpected error during rendering
- Called from `render()` method

**4. ValidationError**

```python
class ValidationError(TemplateError):
    pass
```

**Behavior:**
- Base class for validation-related errors
- No additional attributes or behavior
- Allows catching all validation errors with single except clause

**When Raised:** Never raised directly, only subclasses are raised

**5. MissingVariableError**

```python
class MissingVariableError(ValidationError):
    def __init__(self, missing_variables: list[str], template_name: str | None = None)
```

**Attributes:**
- `missing_variables`: List of missing variable names
- `template_name`: Name of the template (optional)

**Behavior:**
- Formats message with comma-separated list of missing variables
- Format: `"Missing required variables: var1, var2, var3"`

**When Raised:**
- Strict mode enabled and required variables are missing
- Called from `render()` after validation fails
- Also raised when UndefinedError caught from Jinja2

**6. InvalidVariableError**

```python
class InvalidVariableError(ValidationError):
    def __init__(self, variable_name: str, value: Any, reason: str,
                 template_name: str | None = None)
```

**Attributes:**
- `variable_name`: Name of the invalid variable
- `value`: The invalid value
- `reason`: Reason why the value is invalid
- `template_name`: Name of the template (optional)

**Behavior:**
- Formats message with variable name and reason
- Format: `"Invalid value for variable '{variable_name}': {reason}"`

**When Raised:**
- Variable has invalid value (type mismatch, constraint violation)
- Currently not used by Jinja2Renderer (reserved for future use)
- Could be used with `validate_variable_types()`

### Error Contexts

**Context 1: Template Not Found**
- **Trigger:** Template file doesn't exist
- **Exception:** TemplateNotFoundError
- **Methods:** render(), validate(), get_template_variables(), get_template_info()
- **Recovery:** Check template_dir, verify template name, list available templates

**Context 2: Missing Variables (Strict Mode)**
- **Trigger:** Required variables not provided, strict_mode=True
- **Exception:** MissingVariableError
- **Methods:** render()
- **Recovery:** Provide missing variables, disable strict mode, use defaults in template

**Context 3: Rendering Failure**
- **Trigger:** Jinja2 syntax error, runtime error, unexpected exception
- **Exception:** TemplateRenderError
- **Methods:** render()
- **Recovery:** Fix template syntax, check variable values, review original_error

**Context 4: Validation Failure**
- **Trigger:** Template validation fails (non-strict mode)
- **Exception:** None (returns ValidationResult with is_valid=False)
- **Methods:** validate()
- **Recovery:** Check ValidationResult.errors and ValidationResult.warnings

**Context 5: Invalid Variable Value**
- **Trigger:** Variable has wrong type or invalid value
- **Exception:** InvalidVariableError
- **Methods:** Currently unused (reserved for future)
- **Recovery:** Fix variable value, check expected types

### Exception Usage Examples

**Example 1: Handling Template Not Found**
```python
from dotfiles_template_renderer import Jinja2Renderer, TemplateNotFoundError

renderer = Jinja2Renderer("templates")

try:
    result = renderer.render("missing.j2", variables={})
except TemplateNotFoundError as e:
    print(f"Template not found: {e.template_name}")
    print(f"Searched in: {e.search_paths}")
    # Fallback: list available templates
    available = renderer.get_available_templates()
    print(f"Available templates: {available}")
```

**Example 2: Handling Missing Variables**
```python
from dotfiles_template_renderer import Jinja2Renderer, MissingVariableError, RenderConfig

renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    print(f"Missing variables: {e.missing_variables}")
    # Provide missing variables
    all_vars = {"name": "myapp", "version": "1.0.0", "port": 8080}
    result = renderer.render("app.j2", variables=all_vars)
```

**Example 3: Handling Rendering Errors**
```python
from dotfiles_template_renderer import Jinja2Renderer, TemplateRenderError

renderer = Jinja2Renderer("templates")

try:
    result = renderer.render("broken.j2", variables={"data": "value"})
except TemplateRenderError as e:
    print(f"Rendering failed: {e.message}")
    print(f"Template: {e.template_name}")
    if e.original_error:
        print(f"Original error: {e.original_error}")
```

**Example 4: Catching All Template Errors**
```python
from dotfiles_template_renderer import Jinja2Renderer, TemplateError

renderer = Jinja2Renderer("templates")

try:
    result = renderer.render("app.j2", variables={})
except TemplateError as e:
    # Catches all template-related errors
    print(f"Template error: {e}")
    # Handle generically or re-raise
```

**Example 5: Validation Before Rendering**
```python
from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer("templates")

# Validate first (doesn't raise exceptions)
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    print(f"Validation failed:")
    print(f"  Missing: {validation.missing_variables}")
    print(f"  Errors: {validation.errors}")
else:
    # Safe to render
    result = renderer.render("app.j2", variables={"name": "myapp"})
```

### Error Handling Patterns

**Pattern 1: Fail Fast (Strict Mode)**
```python
# Enable strict mode (default)
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))

try:
    result = renderer.render(template_name, variables)
except MissingVariableError as e:
    # Handle missing variables
    logger.error(f"Missing variables: {e.missing_variables}")
    raise
except TemplateError as e:
    # Handle other template errors
    logger.error(f"Template error: {e}")
    raise
```

**Pattern 2: Validate Then Render**
```python
# Validate before rendering
validation = renderer.validate(template_name, variables)

if not validation.is_valid:
    # Handle validation errors without exceptions
    for error in validation.errors:
        logger.error(error)
    for warning in validation.warnings:
        logger.warning(warning)
    return None

# Safe to render
result = renderer.render(template_name, variables)
```

**Pattern 3: Lenient Mode with Defaults**
```python
# Disable strict mode
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))

# Use defaults in template for missing variables
# Template: {{ name | default('unknown') }}
result = renderer.render(template_name, variables)
```

**Pattern 4: Graceful Degradation**
```python
try:
    result = renderer.render(template_name, variables)
except TemplateNotFoundError:
    # Use fallback template
    result = renderer.render("default.j2", variables)
except MissingVariableError as e:
    # Provide defaults for missing variables
    complete_vars = {**default_variables, **variables}
    result = renderer.render(template_name, complete_vars)
except TemplateRenderError:
    # Use static fallback
    result = get_static_fallback()
```

**Pattern 5: Detailed Error Reporting**
```python
try:
    result = renderer.render(template_name, variables)
except TemplateError as e:
    error_report = {
        "error_type": type(e).__name__,
        "message": e.message,
        "template": e.template_name,
    }

    if isinstance(e, MissingVariableError):
        error_report["missing_variables"] = e.missing_variables
    elif isinstance(e, TemplateRenderError):
        error_report["original_error"] = str(e.original_error)

    logger.error(f"Template rendering failed: {error_report}")
    raise
```

### Best Practices

**1. Always Use Strict Mode in Production**
- Catch missing variables early
- Fail fast rather than producing incorrect output
- Use lenient mode only for development/testing

**2. Validate Before Rendering in Critical Paths**
- Use `validate()` before `render()` for important operations
- Check `ValidationResult.is_valid` before proceeding
- Log warnings even if validation passes

**3. Provide Meaningful Error Context**
- Always include template_name when raising exceptions
- Include search_paths for TemplateNotFoundError
- Preserve original_error for TemplateRenderError

**4. Use Specific Exception Handlers**
- Catch specific exceptions (MissingVariableError, TemplateNotFoundError)
- Handle each error type appropriately
- Use generic TemplateError handler as fallback

**5. Log Errors with Full Context**
- Log template name, variables, and error details
- Include stack traces for debugging
- Use structured logging for error reports

**6. Provide Fallbacks for Non-Critical Rendering**
- Use default templates for missing templates
- Provide default variables for missing variables
- Have static fallbacks for rendering failures

**7. Test Error Paths**
- Test missing template scenarios
- Test missing variable scenarios
- Test rendering failure scenarios
- Verify error messages are helpful

---

## Implementation Details

### Concrete Implementations

**Jinja2Renderer (renderers/jinja2.py)**

The production-ready Jinja2 implementation of TemplateRenderer.

**Key Implementation Details:**

1. **Environment Creation (`_create_environment()`)**
   - Creates Jinja2 Environment with FileSystemLoader
   - Configures based on RenderConfig settings
   - Sets StrictUndefined if strict_mode enabled
   - Adds custom filters, tests, and globals
   - Called once during initialization

2. **Rendering (`render()`)**
   - Merges variables dict with kwargs
   - Validates in strict mode before rendering
   - Gets template from environment
   - Renders with merged variables
   - Handles Jinja2 exceptions and wraps them

3. **Validation (`validate()`)**
   - Gets template source code
   - Extracts variables using AST parser
   - Calls validate_variables() utility
   - Returns ValidationResult
   - Handles errors gracefully (returns invalid result)

4. **Variable Extraction (`get_template_variables()`)**
   - Reads template source
   - Uses extract_jinja2_variables() utility
   - Returns sorted list of variables
   - Raises TemplateNotFoundError if template missing

5. **Template Discovery (`get_available_templates()`)**
   - Recursively searches template_dir
   - Filters by extensions: .j2, .jinja, .jinja2
   - Returns relative paths from template_dir
   - Returns sorted list

6. **Template Info (`get_template_info()`)**
   - Checks template exists
   - Gets required variables
   - Gets file size
   - Extracts description from comments
   - Returns TemplateInfo object

7. **Description Extraction (`_extract_description()`)**
   - Reads first 10 lines of template
   - Looks for Jinja2 comments: `{# description #}`
   - Returns first comment found
   - Returns None if no description

8. **Source Retrieval (`_get_template_source()`)**
   - Internal helper to read template file
   - Raises TemplateNotFound if file doesn't exist
   - Used by validate() and get_template_variables()

**Design Patterns Used:**
- **Template Method**: Base class defines workflow, subclass implements details
- **Dependency Injection**: Jinja2 Environment injected via configuration
- **Adapter**: Adapts Jinja2 API to TemplateRenderer interface
- **Facade**: Simplifies Jinja2 complexity behind clean interface

### Utility Functions

**validators.py Module**

**1. extract_jinja2_variables(template_source, env)**

```python
def extract_jinja2_variables(template_source: str, env: Environment) -> set[str]
```

**Purpose:** Extract all variables from a Jinja2 template using AST parsing

**Algorithm:**
1. Parse template source into AST using env.parse()
2. Use jinja2.meta.find_undeclared_variables() to find variables
3. Return set of variable names
4. Fallback to regex if parsing fails

**Why AST Parsing:**
- More accurate than regex
- Handles complex expressions
- Understands Jinja2 syntax
- Excludes loop variables, macros, etc.

**Fallback Behavior:**
- If AST parsing fails, calls extract_variables_regex()
- Ensures function always returns a result
- Logs warning (could be added)

**2. extract_variables_regex(template_source)**

```python
def extract_variables_regex(template_source: str) -> set[str]
```

**Purpose:** Fallback method to extract variables using regex

**Pattern:** `r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)"`

**Matches:**
- `{{ variable }}`
- `{{ variable.attr }}` (captures "variable")
- `{{ variable['key'] }}` (captures "variable")

**Limitations:**
- Doesn't handle complex expressions
- May capture loop variables
- Less accurate than AST parsing

**When Used:**
- AST parsing fails (malformed template)
- Jinja2 environment not available
- Quick variable extraction needed

**3. validate_variables(template_name, required_vars, provided_vars, strict)**

```python
def validate_variables(
    template_name: str,
    required_variables: set[str],
    provided_variables: dict[str, Any],
    strict: bool = True,
) -> ValidationResult
```

**Purpose:** Validate that all required variables are provided

**Algorithm:**
1. Convert provided_variables keys to set
2. Calculate missing = required - provided
3. Calculate unused = provided - required
4. Generate errors if missing and strict=True
5. Generate warnings if missing and strict=False
6. Generate warnings if unused variables
7. Return ValidationResult

**Validation Logic:**
- **Strict Mode:** Missing variables → errors → is_valid=False
- **Lenient Mode:** Missing variables → warnings → is_valid=True
- **Always:** Unused variables → warnings

**Return Value:**
- is_valid: True if no errors
- missing_variables: Sorted list of missing vars
- unused_variables: Sorted list of unused vars
- required_variables: Sorted list of all required vars
- errors: List of error messages
- warnings: List of warning messages

**4. validate_variable_types(variables, expected_types)**

```python
def validate_variable_types(
    variables: dict[str, Any],
    expected_types: dict[str, type] | None = None,
) -> list[str]
```

**Purpose:** Validate variable types against expected types

**Algorithm:**
1. Return empty list if no expected_types
2. For each expected type:
   - Check if variable exists
   - Check isinstance(value, expected_type)
   - Add error message if type mismatch
3. Return list of error messages

**Usage:**
- Currently not used by Jinja2Renderer
- Available for custom validation
- Could be integrated into validate() method

**Example:**
```python
errors = validate_variable_types(
    variables={"port": "8080", "debug": True},
    expected_types={"port": int, "debug": bool}
)
# Returns: ["Variable 'port' has type str, expected int"]
```

### Helper Modules

**core/ Package**

The core package contains the foundational components:

**base.py:**
- TemplateRenderer ABC
- Defines the contract for all renderers
- Provides concrete helper methods (render_from_context, render_to_file)

**exceptions.py:**
- Complete exception hierarchy
- All template-related exceptions
- Consistent error formatting

**types.py:**
- All dataclasses for configuration and results
- Type-safe data structures
- Default values and field factories

**__init__.py:**
- Exports all core components
- Organized by category
- Clean public API

**renderers/ Package**

The renderers package contains concrete implementations:

**jinja2.py:**
- Jinja2Renderer implementation
- Production-ready renderer
- Full feature support

**__init__.py:**
- Exports all renderer implementations
- Currently only Jinja2Renderer
- Extensible for future renderers

**validators.py Module**

Standalone validation utilities:
- Variable extraction functions
- Validation functions
- Type checking functions
- Reusable across renderers

### Code Walkthroughs

**Walkthrough 1: Basic Rendering Flow**

```python
# 1. User creates renderer
renderer = Jinja2Renderer(template_dir="templates", config=RenderConfig(strict_mode=True))

# 2. Jinja2Renderer.__init__() calls super().__init__()
#    - Converts template_dir to Path
#    - Validates directory exists
#    - Stores config (or creates default)

# 3. Jinja2Renderer.__init__() calls _create_environment()
#    - Creates Jinja2 Environment with FileSystemLoader
#    - Configures based on RenderConfig
#    - Adds custom filters/tests/globals
#    - Stores in self._env

# 4. User calls render()
result = renderer.render("app.j2", variables={"name": "myapp", "version": "1.0"})

# 5. render() merges variables with kwargs
all_variables = {**variables, **kwargs}  # {"name": "myapp", "version": "1.0"}

# 6. render() validates if strict_mode
validation = self.validate("app.j2", all_variables)
if not validation.is_valid:
    raise MissingVariableError(validation.missing_variables, "app.j2")

# 7. validate() extracts template variables
template_source = self._get_template_source("app.j2")
required_vars = extract_jinja2_variables(template_source, self._env)

# 8. validate() calls validate_variables()
validation_result = validate_variables("app.j2", required_vars, all_variables, strict=True)

# 9. Back to render(): validation passed, get template
template = self._env.get_template("app.j2")

# 10. Render template with variables
rendered = template.render(**all_variables)

# 11. Return rendered string
return rendered  # "FROM python:3.12\nLABEL name=myapp\n..."
```

**Walkthrough 2: Validation Flow**

```python
# 1. User calls validate()
validation = renderer.validate("app.j2", variables={"name": "myapp"})

# 2. validate() gets template source
template_source = self._get_template_source("app.j2")
# Returns: "FROM {{ base_image }}\nLABEL name={{ name }}\n..."

# 3. validate() extracts variables using AST
required_vars = extract_jinja2_variables(template_source, self._env)
# Returns: {"base_image", "name"}

# 4. validate() calls validate_variables()
result = validate_variables(
    template_name="app.j2",
    required_variables={"base_image", "name"},
    provided_variables={"name": "myapp"},
    strict=True
)

# 5. validate_variables() calculates differences
provided_keys = {"name"}
missing = {"base_image", "name"} - {"name"} = {"base_image"}
unused = {"name"} - {"base_image", "name"} = {}

# 6. validate_variables() generates errors (strict mode)
errors = ["Missing required variables: base_image"]
warnings = []

# 7. validate_variables() returns ValidationResult
return ValidationResult(
    is_valid=False,
    missing_variables=["base_image"],
    unused_variables=[],
    required_variables=["base_image", "name"],
    errors=["Missing required variables: base_image"],
    warnings=[]
)

# 8. User checks validation result
if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")  # ["base_image"]
```

**Walkthrough 3: Template Discovery Flow**

```python
# 1. User calls get_available_templates()
templates = renderer.get_available_templates()

# 2. get_available_templates() searches template_dir recursively
templates = []
for path in self.template_dir.rglob("*"):
    # Finds: templates/app.j2, templates/configs/nginx.j2, templates/README.md

# 3. Filters by extension
    if path.is_file() and path.suffix in [".j2", ".jinja", ".jinja2"]:
        # Keeps: templates/app.j2, templates/configs/nginx.j2
        # Skips: templates/README.md

# 4. Gets relative path from template_dir
        rel_path = path.relative_to(self.template_dir)
        # "app.j2", "configs/nginx.j2"

# 5. Adds to list
        templates.append(str(rel_path))

# 6. Returns sorted list
return sorted(templates)  # ["app.j2", "configs/nginx.j2"]
```

### Implementation Patterns

**Pattern 1: Validation Before Action**
- Always validate before performing risky operations
- Used in render() to validate before rendering
- Prevents partial failures and inconsistent state

**Pattern 2: Graceful Degradation**
- AST parsing with regex fallback
- Return invalid ValidationResult instead of raising exception
- Allows caller to decide how to handle errors

**Pattern 3: Separation of Concerns**
- Validators module separate from renderer
- Core abstractions separate from implementations
- Each module has single responsibility

**Pattern 4: Configuration Over Code**
- RenderConfig controls behavior
- No hardcoded settings
- Easy to customize without subclassing

**Pattern 5: Explicit Error Handling**
- Catch specific Jinja2 exceptions
- Wrap in domain-specific exceptions
- Preserve original error for debugging

**Pattern 6: Immutable Configuration**
- RenderConfig is dataclass (immutable by convention)
- Temporary config override in render_from_context()
- Always restore original config

**Pattern 7: Sorted Results**
- All list returns are sorted
- Consistent ordering for testing
- Predictable behavior

### Internal APIs

**Private Methods in Jinja2Renderer:**

**_create_environment() -> Environment**
- Creates and configures Jinja2 Environment
- Called once during initialization
- Returns configured Environment instance

**_get_template_source(template_name: str) -> str**
- Reads template file content
- Raises TemplateNotFound if file doesn't exist
- Used by validate() and get_template_variables()

**_extract_description(template_path: Path) -> str | None**
- Extracts description from template comments
- Looks for `{# description #}` in first 10 lines
- Returns None if no description found
- Used by get_template_info()

**Internal Attributes:**

**self.template_dir: Path**
- Path to template directory
- Set by base class __init__()
- Used for all file operations

**self.config: RenderConfig**
- Rendering configuration
- Set by base class __init__()
- Used to configure Jinja2 Environment

**self._env: Environment**
- Jinja2 Environment instance
- Created by _create_environment()
- Used for all template operations

**Naming Conventions:**
- Private methods: Prefix with `_`
- Internal attributes: Prefix with `_` (except template_dir, config)
- Public methods: No prefix
- Abstract methods: Defined in base class

---

## Key Features & Capabilities

### Unique Features

**1. Template Agnosticism**
- Not tied to any specific content type (Dockerfiles, configs, scripts, etc.)
- Generic rendering engine for any text-based template
- Reusable across different use cases in the project

**2. Strict Validation Mode**
- Validates all variables before rendering
- Fails fast on missing variables
- Prevents generating invalid output
- Configurable (can be disabled for lenient mode)

**3. Template Introspection**
- Discover what variables a template requires without rendering
- List all available templates in a directory
- Get detailed metadata about templates
- Useful for dynamic template selection and validation

**4. Variable Extraction via AST**
- Uses Jinja2's AST parser for accurate variable extraction
- More reliable than regex-based extraction
- Handles complex expressions correctly
- Fallback to regex if parsing fails

**5. Flexible Configuration**
- Comprehensive RenderConfig for customization
- Custom Jinja2 filters, tests, and globals
- Control over whitespace handling
- Autoescape support for HTML/XML

**6. Context-Based Rendering**
- TemplateContext encapsulates rendering parameters
- Allows passing rendering jobs as objects
- Supports temporary config overrides
- Useful for pipeline integration

**7. File Output Support**
- render_to_file() method for direct file output
- Automatically creates parent directories
- Atomic write operation
- Convenient for generating configuration files

**8. Comprehensive Error Handling**
- Detailed exception hierarchy
- Preserves original errors for debugging
- Meaningful error messages with context
- Graceful error handling in validation

**9. Extensible Design**
- Abstract base class allows multiple implementations
- Easy to add new template engines (Mako, Mustache, etc.)
- Validators module is renderer-agnostic
- Clean separation of concerns

**10. Type Safety**
- Full type hints throughout
- Dataclasses for configuration and results
- Type-safe API
- IDE autocomplete support

### Feature Implementation Details

**Feature 1: Strict Validation**

**Implementation:**
```python
# In render() method
if self.config.strict_mode:
    validation = self.validate(template_name, all_variables)
    if not validation.is_valid:
        raise MissingVariableError(validation.missing_variables, template_name)
```

**How It Works:**
1. Check if strict_mode enabled in config
2. Call validate() before rendering
3. Raise MissingVariableError if validation fails
4. Only render if validation passes

**Configuration:**
```python
# Enable strict mode (default)
config = RenderConfig(strict_mode=True)

# Disable for lenient mode
config = RenderConfig(strict_mode=False)
```

**Feature 2: Template Introspection**

**Implementation:**
```python
# get_template_variables() extracts variables
template_source = self._get_template_source(template_name)
variables = extract_jinja2_variables(template_source, self._env)
return sorted(variables)

# get_template_info() provides metadata
return TemplateInfo(
    name=template_name,
    path=template_path,
    size=template_path.stat().st_size,
    required_variables=self.get_template_variables(template_name),
    description=self._extract_description(template_path),
)
```

**Use Cases:**
- Dynamic template selection based on requirements
- Pre-validation before rendering
- Template documentation generation
- IDE integration for template editing

**Feature 3: AST-Based Variable Extraction**

**Implementation:**
```python
def extract_jinja2_variables(template_source: str, env: Environment) -> set[str]:
    try:
        # Parse template into AST
        ast = env.parse(template_source)
        # Find undeclared variables
        return meta.find_undeclared_variables(ast)
    except Exception:
        # Fallback to regex
        return extract_variables_regex(template_source)
```

**Why AST:**
- Understands Jinja2 syntax
- Excludes loop variables ({% for item in items %})
- Excludes macro parameters
- Handles complex expressions
- More accurate than regex

**Fallback:**
- Regex pattern: `r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)"`
- Used when AST parsing fails
- Less accurate but always works

**Feature 4: Custom Filters/Tests/Globals**

**Implementation:**
```python
# In _create_environment()
if self.config.custom_filters:
    env.filters.update(self.config.custom_filters)
if self.config.custom_tests:
    env.tests.update(self.config.custom_tests)
if self.config.custom_globals:
    env.globals.update(self.config.custom_globals)
```

**Usage:**
```python
def uppercase_filter(text):
    return text.upper()

def is_even_test(n):
    return n % 2 == 0

config = RenderConfig(
    custom_filters={"uppercase": uppercase_filter},
    custom_tests={"even": is_even_test},
    custom_globals={"pi": 3.14159},
)

renderer = Jinja2Renderer("templates", config=config)

# In template:
# {{ name | uppercase }}
# {% if port is even %}
# {{ pi }}
```

**Feature 5: Context-Based Rendering**

**Implementation:**
```python
def render_from_context(self, context: TemplateContext) -> str:
    # Temporarily override config
    original_config = self.config
    if context.config:
        self.config = context.config

    try:
        return self.render(context.template_name, context.variables)
    finally:
        # Always restore original config
        self.config = original_config
```

**Usage:**
```python
context = TemplateContext(
    template_name="app.j2",
    variables={"name": "myapp"},
    config=RenderConfig(strict_mode=False),  # Override for this render
)

result = renderer.render_from_context(context)
```

**Feature 6: File Output**

**Implementation:**
```python
def render_to_file(self, template_name, output_path, variables, **kwargs):
    # Render template
    rendered = self.render(template_name, variables, **kwargs)

    # Create parent directories
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    output_path.write_text(rendered)
```

**Usage:**
```python
renderer.render_to_file(
    "nginx.conf.j2",
    "/etc/nginx/sites-available/mysite",
    variables={"server_name": "example.com", "port": 80}
)
```

### Benefits & Trade-offs

**Benefit 1: Template Agnosticism**
- ✅ Reusable across different content types
- ✅ Single module for all template rendering needs
- ✅ Easier to maintain and test
- ⚠️ May be overkill for simple string formatting
- ⚠️ Requires understanding Jinja2 syntax

**Benefit 2: Strict Validation**
- ✅ Catches errors early (fail fast)
- ✅ Prevents generating invalid output
- ✅ Better error messages
- ⚠️ Requires all variables upfront
- ⚠️ Can't use template defaults in strict mode
- 💡 Solution: Use lenient mode with template defaults

**Benefit 3: AST-Based Extraction**
- ✅ More accurate than regex
- ✅ Handles complex expressions
- ✅ Understands Jinja2 semantics
- ⚠️ Requires valid Jinja2 syntax
- ⚠️ Slower than regex
- 💡 Fallback to regex ensures robustness

**Benefit 4: Extensible Design**
- ✅ Easy to add new template engines
- ✅ Clean separation of concerns
- ✅ Testable components
- ⚠️ More complex than single implementation
- ⚠️ Abstract base class adds indirection
- 💡 Worth it for long-term maintainability

**Benefit 5: Type Safety**
- ✅ IDE autocomplete and type checking
- ✅ Catches type errors at development time
- ✅ Self-documenting code
- ⚠️ More verbose than dynamic typing
- ⚠️ Requires Python 3.10+ for modern syntax
- 💡 Improves code quality and maintainability

**Benefit 6: Comprehensive Error Handling**
- ✅ Detailed error messages
- ✅ Preserves original errors
- ✅ Allows graceful error handling
- ⚠️ More exception types to handle
- ⚠️ Requires understanding exception hierarchy
- 💡 Use generic TemplateError handler as fallback

**Trade-off: Strict Mode vs. Lenient Mode**

**Strict Mode (default):**
- ✅ Fail fast on missing variables
- ✅ Catch errors early
- ✅ Prevent invalid output
- ⚠️ Requires all variables upfront
- ⚠️ Can't use template defaults

**Lenient Mode:**
- ✅ Allows template defaults
- ✅ More flexible
- ✅ Useful for development
- ⚠️ May generate invalid output
- ⚠️ Errors caught later (at runtime)

**Recommendation:** Use strict mode in production, lenient mode in development

**Trade-off: Validation Before Rendering**

**With Validation:**
- ✅ Catch errors before rendering
- ✅ Better error messages
- ✅ No partial rendering
- ⚠️ Extra overhead (parse template twice)
- ⚠️ Slower for large templates

**Without Validation:**
- ✅ Faster rendering
- ✅ Single pass through template
- ⚠️ Errors during rendering
- ⚠️ May produce partial output

**Recommendation:** Validate in strict mode, skip in lenient mode (current implementation)

**Trade-off: AST vs. Regex Extraction**

**AST Parsing:**
- ✅ More accurate
- ✅ Handles complex expressions
- ✅ Understands Jinja2 semantics
- ⚠️ Requires valid syntax
- ⚠️ Slower

**Regex Extraction:**
- ✅ Faster
- ✅ Works with invalid syntax
- ✅ Simple implementation
- ⚠️ Less accurate
- ⚠️ May miss variables

**Recommendation:** Use AST with regex fallback (current implementation)

---

## Integration & Usage Patterns

### Common Usage Patterns

**Pattern 1: Basic Template Rendering**
```python
from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer(template_dir="templates")
result = renderer.render("app.j2", variables={"name": "myapp", "version": "1.0"})
print(result)
```

**Pattern 2: Strict Validation**
```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig, MissingVariableError

renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except MissingVariableError as e:
    print(f"Missing: {e.missing_variables}")
    # Provide missing variables
    result = renderer.render("app.j2", variables={"name": "myapp", "version": "1.0"})
```

**Pattern 3: Pre-Validation**
```python
renderer = Jinja2Renderer("templates")

# Validate before rendering
validation = renderer.validate("app.j2", variables={"name": "myapp"})

if not validation.is_valid:
    print(f"Missing: {validation.missing_variables}")
    print(f"Required: {validation.required_variables}")
else:
    result = renderer.render("app.j2", variables={"name": "myapp"})
```

**Pattern 4: Template Discovery**
```python
renderer = Jinja2Renderer("templates")

# List all templates
templates = renderer.get_available_templates()
for template in templates:
    print(f"- {template}")

# Get template info
info = renderer.get_template_info("app.j2")
print(f"Variables: {info.required_variables}")
print(f"Size: {info.size} bytes")
```

**Pattern 5: Variable Introspection**
```python
renderer = Jinja2Renderer("templates")

# Discover required variables
variables = renderer.get_template_variables("app.j2")
print(f"Required: {variables}")

# Prepare variables dynamically
user_vars = {}
for var in variables:
    user_vars[var] = input(f"Enter {var}: ")

result = renderer.render("app.j2", variables=user_vars)
```

**Pattern 6: Custom Filters**
```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig

def uppercase_filter(text):
    return text.upper()

def format_size_filter(bytes):
    return f"{bytes / 1024:.2f} KB"

config = RenderConfig(
    custom_filters={
        "uppercase": uppercase_filter,
        "format_size": format_size_filter,
    }
)

renderer = Jinja2Renderer("templates", config=config)

# In template: {{ name | uppercase }}, {{ size | format_size }}
result = renderer.render("app.j2", variables={"name": "myapp", "size": 2048})
```

**Pattern 7: Render to File**
```python
renderer = Jinja2Renderer("templates")

# Render and save to file
renderer.render_to_file(
    "nginx.conf.j2",
    "/etc/nginx/sites-available/mysite",
    variables={"server_name": "example.com", "port": 80}
)
```

**Pattern 8: Context-Based Rendering**
```python
from dotfiles_template_renderer import Jinja2Renderer, TemplateContext, RenderConfig

renderer = Jinja2Renderer("templates")

# Create context with custom config
context = TemplateContext(
    template_name="app.j2",
    variables={"name": "myapp"},
    config=RenderConfig(strict_mode=False)  # Override for this render
)

result = renderer.render_from_context(context)
```

**Pattern 9: Batch Rendering**
```python
renderer = Jinja2Renderer("templates")

templates_to_render = [
    ("app.j2", {"name": "app1", "version": "1.0"}),
    ("config.j2", {"env": "production", "debug": False}),
    ("script.j2", {"command": "start", "args": ["--verbose"]}),
]

results = {}
for template_name, variables in templates_to_render:
    results[template_name] = renderer.render(template_name, variables)
```

**Pattern 10: Template Selection**
```python
renderer = Jinja2Renderer("templates")

# Select template based on criteria
def select_template(app_type):
    templates = {
        "python": "python.j2",
        "node": "node.j2",
        "rust": "rust.j2",
    }
    return templates.get(app_type, "default.j2")

template_name = select_template("python")
result = renderer.render(template_name, variables={"name": "myapp"})
```

**Pattern 11: Lenient Mode with Defaults**
```python
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))

# Template can use defaults: {{ version | default('1.0.0') }}
result = renderer.render("app.j2", variables={"name": "myapp"})
# Works even if 'version' not provided
```

**Pattern 12: Error Handling with Fallback**
```python
from dotfiles_template_renderer import Jinja2Renderer, TemplateError

renderer = Jinja2Renderer("templates")

try:
    result = renderer.render("app.j2", variables={"name": "myapp"})
except TemplateError as e:
    print(f"Error: {e}")
    # Use fallback template
    result = renderer.render("default.j2", variables={"name": "myapp"})
```

### Integration with Other Modules

**Integration 1: Pipeline Steps (pipeline_steps.container_steps)**

```python
# From: src/dotfiles-installer/cli/src/pipeline_steps/container_steps.py

from dotfiles_template_renderer import Jinja2Renderer, RenderConfig
from src.modules.pipeline.core.types import PipelineContext, PipelineStep

class RenderTemplateStep(PipelineStep):
    """Pipeline step to render a Jinja2 template."""

    def __init__(self, template_name, template_dir, variables, output_key, strict_mode=True):
        self.template_name = template_name
        self.template_dir = template_dir
        self.variables = variables
        self.output_key = output_key
        self.strict_mode = strict_mode

    def run(self, context: PipelineContext) -> PipelineContext:
        # Create renderer
        renderer = Jinja2Renderer(
            self.template_dir,
            config=RenderConfig(strict_mode=self.strict_mode),
        )

        # Render template
        rendered = renderer.render(self.template_name, self.variables)

        # Store in context
        context.results[self.output_key] = rendered

        return context
```

**Usage in Pipeline:**
```python
from src.modules.pipeline import Pipeline
from src.pipeline_steps.container_steps import RenderTemplateStep

step = RenderTemplateStep(
    template_name="Dockerfile.j2",
    template_dir="templates",
    variables={"base_image": "python:3.12", "workdir": "/app"},
    output_key="dockerfile",
)

pipeline = Pipeline.create([step])
context = pipeline.run(context)

dockerfile = context.results["dockerfile"]
```

**Integration 2: Container Manager Module**

The template_renderer is used to render Dockerfiles before passing to container_manager:

```python
from dotfiles_template_renderer import Jinja2Renderer
from dotfiles_container_manager import DockerManager, BuildContext

# Render Dockerfile
renderer = Jinja2Renderer("templates")
dockerfile = renderer.render("python.j2", variables={
    "base_image": "python:3.12-slim",
    "workdir": "/app",
    "system_packages": ["git", "curl"],
})

# Pass to container manager
manager = DockerManager()
build_context = BuildContext(
    dockerfile_content=dockerfile,  # Rendered content
    context_dir=Path("."),
    tag="myapp:latest",
)

manager.build_image(build_context)
```

**Integration 3: Configuration File Generation**

```python
from dotfiles_template_renderer import Jinja2Renderer
from pathlib import Path

renderer = Jinja2Renderer("config_templates")

# Render multiple config files
configs = {
    "nginx.conf": {"server_name": "example.com", "port": 80},
    "app.yaml": {"env": "production", "debug": False},
    "database.ini": {"host": "localhost", "port": 5432},
}

for template_name, variables in configs.items():
    output_path = Path("/etc/myapp") / template_name
    renderer.render_to_file(f"{template_name}.j2", output_path, variables)
```

**Integration 4: Dynamic Template Selection**

```python
from dotfiles_template_renderer import Jinja2Renderer

class TemplateManager:
    def __init__(self, template_dir):
        self.renderer = Jinja2Renderer(template_dir)

    def render_for_platform(self, platform, variables):
        """Render template based on platform."""
        template_map = {
            "linux": "linux.j2",
            "macos": "macos.j2",
            "windows": "windows.j2",
        }
        template_name = template_map.get(platform, "default.j2")
        return self.renderer.render(template_name, variables)

    def list_templates_for_category(self, category):
        """List templates in a category."""
        all_templates = self.renderer.get_available_templates()
        return [t for t in all_templates if t.startswith(f"{category}/")]
```

### Typical Workflows

**Workflow 1: Generate Dockerfile from Template**

```python
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig
from pathlib import Path

# 1. Create renderer
renderer = Jinja2Renderer(
    template_dir="docker/templates",
    config=RenderConfig(strict_mode=True)
)

# 2. Prepare variables
variables = {
    "base_image": "python:3.12-slim",
    "workdir": "/app",
    "system_packages": ["git", "curl", "build-essential"],
    "python_packages": ["flask", "requests", "pytest"],
    "env_vars": {"PYTHONUNBUFFERED": "1", "ENV": "production"},
    "entrypoint": ["python"],
    "cmd": ["app.py"],
}

# 3. Validate variables
validation = renderer.validate("python.j2", variables)
if not validation.is_valid:
    raise ValueError(f"Missing variables: {validation.missing_variables}")

# 4. Render template
dockerfile = renderer.render("python.j2", variables)

# 5. Save to file
output_path = Path("Dockerfile")
output_path.write_text(dockerfile)

print(f"Generated Dockerfile ({len(dockerfile)} bytes)")
```

**Workflow 2: Batch Configuration Generation**

```python
from dotfiles_template_renderer import Jinja2Renderer
from pathlib import Path

# 1. Create renderer
renderer = Jinja2Renderer("config_templates")

# 2. Define configurations
environments = {
    "development": {
        "debug": True,
        "log_level": "DEBUG",
        "database_host": "localhost",
    },
    "staging": {
        "debug": False,
        "log_level": "INFO",
        "database_host": "staging-db.example.com",
    },
    "production": {
        "debug": False,
        "log_level": "WARNING",
        "database_host": "prod-db.example.com",
    },
}

# 3. Render for each environment
for env_name, env_vars in environments.items():
    output_path = Path(f"config/{env_name}.yaml")
    renderer.render_to_file("app.yaml.j2", output_path, env_vars)
    print(f"Generated {output_path}")
```

**Workflow 3: Interactive Template Rendering**

```python
from dotfiles_template_renderer import Jinja2Renderer

# 1. Create renderer
renderer = Jinja2Renderer("templates")

# 2. List available templates
templates = renderer.get_available_templates()
print("Available templates:")
for i, template in enumerate(templates, 1):
    print(f"{i}. {template}")

# 3. Select template
choice = int(input("Select template: ")) - 1
template_name = templates[choice]

# 4. Get required variables
required_vars = renderer.get_template_variables(template_name)
print(f"\nRequired variables: {required_vars}")

# 5. Collect variables from user
variables = {}
for var in required_vars:
    variables[var] = input(f"Enter {var}: ")

# 6. Render template
result = renderer.render(template_name, variables)

# 7. Display result
print("\n--- Rendered Output ---")
print(result)
```

**Workflow 4: Template Validation Pipeline**

```python
from dotfiles_template_renderer import Jinja2Renderer
from pathlib import Path

# 1. Create renderer
renderer = Jinja2Renderer("templates")

# 2. Get all templates
templates = renderer.get_available_templates()

# 3. Validate each template
validation_results = {}
for template_name in templates:
    try:
        # Get required variables
        required_vars = renderer.get_template_variables(template_name)

        # Get template info
        info = renderer.get_template_info(template_name)

        validation_results[template_name] = {
            "status": "valid",
            "required_vars": required_vars,
            "size": info.size,
            "description": info.description,
        }
    except Exception as e:
        validation_results[template_name] = {
            "status": "invalid",
            "error": str(e),
        }

# 4. Report results
for template_name, result in validation_results.items():
    if result["status"] == "valid":
        print(f"✅ {template_name}: {len(result['required_vars'])} variables")
    else:
        print(f"❌ {template_name}: {result['error']}")
```

**Workflow 5: Multi-Template Project Generation**

```python
from dotfiles_template_renderer import Jinja2Renderer
from pathlib import Path

# 1. Create renderer
renderer = Jinja2Renderer("project_templates")

# 2. Define project structure
project_files = {
    "README.md": "readme.j2",
    "setup.py": "setup.j2",
    "src/__init__.py": "init.j2",
    "src/main.py": "main.j2",
    "tests/test_main.py": "test.j2",
    ".gitignore": "gitignore.j2",
}

# 3. Prepare variables
variables = {
    "project_name": "myproject",
    "author": "John Doe",
    "version": "0.1.0",
    "description": "My awesome project",
    "python_version": "3.12",
}

# 4. Render all files
project_dir = Path("myproject")
for output_file, template_name in project_files.items():
    output_path = project_dir / output_file
    renderer.render_to_file(template_name, output_path, variables)
    print(f"Created {output_path}")

print(f"\nProject '{variables['project_name']}' created successfully!")
```

### Best Practices

**1. Always Use Strict Mode in Production**
```python
# ✅ Good: Strict mode catches errors early
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))

# ❌ Bad: Lenient mode may produce invalid output
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))
```

**2. Validate Before Rendering Critical Templates**
```python
# ✅ Good: Validate first
validation = renderer.validate(template_name, variables)
if validation.is_valid:
    result = renderer.render(template_name, variables)

# ❌ Bad: Render without validation
result = renderer.render(template_name, variables)  # May fail
```

**3. Use Specific Exception Handlers**
```python
# ✅ Good: Handle specific exceptions
try:
    result = renderer.render(template_name, variables)
except MissingVariableError as e:
    # Handle missing variables
    pass
except TemplateNotFoundError as e:
    # Handle missing template
    pass

# ❌ Bad: Generic exception handler
try:
    result = renderer.render(template_name, variables)
except Exception as e:
    # Too broad
    pass
```

**4. Provide Meaningful Variable Names**
```python
# ✅ Good: Clear variable names
variables = {
    "base_image": "python:3.12",
    "workdir": "/app",
    "system_packages": ["git", "curl"],
}

# ❌ Bad: Unclear variable names
variables = {
    "img": "python:3.12",
    "dir": "/app",
    "pkgs": ["git", "curl"],
}
```

**5. Use Template Comments for Documentation**
```python
# ✅ Good: Document template purpose
# In template:
# {# Dockerfile template for Python applications #}
# FROM {{ base_image }}

# ❌ Bad: No documentation
# FROM {{ base_image }}
```

**6. Organize Templates by Category**
```
# ✅ Good: Organized structure
templates/
├── dockerfiles/
│   ├── python.j2
│   ├── node.j2
│   └── rust.j2
├── configs/
│   ├── nginx.j2
│   └── app.j2
└── scripts/
    └── deploy.j2

# ❌ Bad: Flat structure
templates/
├── python.j2
├── node.j2
├── nginx.j2
├── app.j2
└── deploy.j2
```

**7. Use Default Values in Templates**
```python
# ✅ Good: Provide defaults for optional variables
# {{ version | default('1.0.0') }}
# {{ debug | default(false) }}

# ❌ Bad: No defaults for optional variables
# {{ version }}
# {{ debug }}
```

**8. Log Rendering Operations**
```python
# ✅ Good: Log rendering operations
logger.info(f"Rendering template: {template_name}")
result = renderer.render(template_name, variables)
logger.info(f"Rendered {len(result)} bytes")

# ❌ Bad: No logging
result = renderer.render(template_name, variables)
```

### Anti-patterns

**Anti-pattern 1: Hardcoding Template Directory**
```python
# ❌ Bad: Hardcoded path
renderer = Jinja2Renderer("/absolute/path/to/templates")

# ✅ Good: Configurable path
from pathlib import Path
template_dir = Path(__file__).parent / "templates"
renderer = Jinja2Renderer(template_dir)
```

**Anti-pattern 2: Ignoring Validation Results**
```python
# ❌ Bad: Ignore validation
validation = renderer.validate(template_name, variables)
result = renderer.render(template_name, variables)  # Render anyway

# ✅ Good: Check validation
validation = renderer.validate(template_name, variables)
if validation.is_valid:
    result = renderer.render(template_name, variables)
```

**Anti-pattern 3: Catching and Swallowing Exceptions**
```python
# ❌ Bad: Swallow exceptions
try:
    result = renderer.render(template_name, variables)
except Exception:
    pass  # Silent failure

# ✅ Good: Handle or re-raise
try:
    result = renderer.render(template_name, variables)
except TemplateError as e:
    logger.error(f"Rendering failed: {e}")
    raise
```

**Anti-pattern 4: Not Using Type Hints**
```python
# ❌ Bad: No type hints
def render_template(renderer, template, vars):
    return renderer.render(template, vars)

# ✅ Good: Use type hints
def render_template(
    renderer: Jinja2Renderer,
    template: str,
    variables: dict[str, Any]
) -> str:
    return renderer.render(template, variables)
```

**Anti-pattern 5: Creating Renderer Per Render**
```python
# ❌ Bad: Create renderer for each render
for template in templates:
    renderer = Jinja2Renderer("templates")  # Wasteful
    result = renderer.render(template, variables)

# ✅ Good: Reuse renderer
renderer = Jinja2Renderer("templates")
for template in templates:
    result = renderer.render(template, variables)
```

**Anti-pattern 6: Not Handling Missing Templates**
```python
# ❌ Bad: Assume template exists
result = renderer.render("missing.j2", variables)  # May crash

# ✅ Good: Check template exists
templates = renderer.get_available_templates()
if "missing.j2" in templates:
    result = renderer.render("missing.j2", variables)
else:
    result = renderer.render("default.j2", variables)
```

**Anti-pattern 7: Mixing Template Logic with Business Logic**
```python
# ❌ Bad: Complex logic in template
# {% if user.age > 18 and user.country == 'US' and user.verified %}

# ✅ Good: Prepare data in Python
variables = {
    "can_access": user.age > 18 and user.country == 'US' and user.verified
}
# {% if can_access %}
```

---

## Advanced Topics

### Security Considerations

**1. Template Injection Attacks**

**Risk:** User-controlled template content can execute arbitrary code

**Mitigation:**
```python
# ❌ NEVER: Allow user-controlled template content
user_template = request.get("template")  # From user input
renderer.render_string(user_template, variables)  # DANGEROUS!

# ✅ ALWAYS: Use predefined templates only
template_name = request.get("template_name")
if template_name in allowed_templates:
    renderer.render(template_name, variables)
```

**Best Practice:**
- Never render user-provided template strings
- Only allow selection from predefined templates
- Validate template names against whitelist
- Use template_dir to restrict template locations

**2. Variable Injection**

**Risk:** User-controlled variables can inject malicious content

**Mitigation:**
```python
# Enable autoescape for HTML/XML templates
config = RenderConfig(autoescape=True)
renderer = Jinja2Renderer("templates", config=config)

# In template: {{ user_input }} will be escaped
# <script>alert('xss')</script> → &lt;script&gt;alert('xss')&lt;/script&gt;
```

**Best Practice:**
- Enable autoescape for HTML/XML templates
- Validate and sanitize user inputs before passing to templates
- Use Jinja2's |safe filter only for trusted content
- Implement input validation for all variables

**3. Path Traversal**

**Risk:** Malicious template names can access files outside template_dir

**Mitigation:**
```python
# ✅ Good: Jinja2 FileSystemLoader prevents path traversal
renderer = Jinja2Renderer("templates")
renderer.render("../../etc/passwd", {})  # Raises TemplateNotFoundError

# Additional validation
def validate_template_name(template_name: str) -> bool:
    # Reject paths with .. or absolute paths
    return ".." not in template_name and not Path(template_name).is_absolute()

if validate_template_name(template_name):
    renderer.render(template_name, variables)
```

**Best Practice:**
- Jinja2's FileSystemLoader already prevents path traversal
- Additional validation for defense in depth
- Never use absolute paths in template names
- Restrict template_dir permissions

**4. Information Disclosure**

**Risk:** Templates may expose sensitive information in errors

**Mitigation:**
```python
# ✅ Good: Catch and sanitize errors
try:
    result = renderer.render(template_name, variables)
except TemplateError as e:
    # Log full error for debugging
    logger.error(f"Template error: {e}", exc_info=True)
    # Return sanitized error to user
    return "An error occurred while rendering the template"
```

**Best Practice:**
- Don't expose full error messages to users
- Log detailed errors for debugging
- Use generic error messages in production
- Sanitize stack traces

**5. Resource Exhaustion**

**Risk:** Large templates or complex expressions can cause DoS

**Mitigation:**
```python
# Set limits on template size
MAX_TEMPLATE_SIZE = 1024 * 1024  # 1 MB

def validate_template_size(template_path: Path) -> bool:
    return template_path.stat().st_size <= MAX_TEMPLATE_SIZE

# Set timeout for rendering (requires custom implementation)
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Template rendering timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)  # 5 second timeout
try:
    result = renderer.render(template_name, variables)
finally:
    signal.alarm(0)
```

**Best Practice:**
- Limit template file sizes
- Set rendering timeouts
- Monitor resource usage
- Rate limit template rendering requests

### Performance Considerations

**1. Template Caching**

**Current Behavior:**
- Jinja2 Environment caches compiled templates automatically
- Templates are compiled once and reused
- Cache is per-renderer instance

**Optimization:**
```python
# ✅ Good: Reuse renderer instance
renderer = Jinja2Renderer("templates")
for i in range(1000):
    result = renderer.render("app.j2", variables)  # Uses cached template

# ❌ Bad: Create new renderer each time
for i in range(1000):
    renderer = Jinja2Renderer("templates")  # Recompiles template each time
    result = renderer.render("app.j2", variables)
```

**Best Practice:**
- Create renderer once and reuse
- Share renderer across requests (thread-safe)
- Don't create renderer per render operation

**2. Variable Validation Overhead**

**Cost:** Validation parses template twice (once for validation, once for rendering)

**Optimization:**
```python
# Strict mode: Validates before rendering
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))
result = renderer.render(template_name, variables)  # Parses twice

# Lenient mode: No validation, single parse
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))
result = renderer.render(template_name, variables)  # Parses once
```

**Trade-off:**
- Strict mode: Safer but slower (2x parse)
- Lenient mode: Faster but less safe (1x parse)

**Recommendation:**
- Use strict mode in development/testing
- Consider lenient mode for high-performance production (with good tests)
- Cache validation results if rendering same template multiple times

**3. Large Template Files**

**Impact:** Large templates take longer to parse and render

**Optimization:**
```python
# ✅ Good: Split large templates into smaller includes
# main.j2:
# {% include 'header.j2' %}
# {% include 'body.j2' %}
# {% include 'footer.j2' %}

# ❌ Bad: Single large template
# main.j2: 10,000 lines
```

**Best Practice:**
- Split large templates into smaller includes
- Use template inheritance for common structure
- Keep templates focused and modular

**4. Complex Expressions**

**Impact:** Complex Jinja2 expressions slow down rendering

**Optimization:**
```python
# ✅ Good: Prepare data in Python
variables = {
    "formatted_date": datetime.now().strftime("%Y-%m-%d"),
    "user_display_name": f"{user.first_name} {user.last_name}",
    "is_admin": user.role == "admin" and user.verified,
}

# ❌ Bad: Complex logic in template
# {{ now().strftime("%Y-%m-%d") }}
# {{ user.first_name + " " + user.last_name }}
# {{ user.role == "admin" and user.verified }}
```

**Best Practice:**
- Do complex calculations in Python
- Pass prepared data to templates
- Keep template logic simple

**5. Rendering Frequency**

**Optimization for High-Frequency Rendering:**
```python
# Cache rendered results if variables don't change
from functools import lru_cache

@lru_cache(maxsize=128)
def render_cached(template_name: str, variables_tuple: tuple) -> str:
    variables = dict(variables_tuple)
    return renderer.render(template_name, variables)

# Convert dict to tuple for caching
variables_tuple = tuple(sorted(variables.items()))
result = render_cached(template_name, variables_tuple)
```

**Best Practice:**
- Cache rendered results for static content
- Use CDN for frequently accessed rendered content
- Consider pre-rendering at build time

**Performance Benchmarks:**

```python
# Typical performance (approximate):
# - Template compilation: 1-5ms (cached after first use)
# - Variable extraction (AST): 0.5-2ms
# - Validation: 1-3ms
# - Rendering (simple template): 0.1-1ms
# - Rendering (complex template): 1-10ms

# Total for first render (strict mode): 3-20ms
# Total for subsequent renders (strict mode): 1-13ms
# Total for subsequent renders (lenient mode): 0.1-10ms
```

### Extensibility Points

**1. Adding New Template Engines**

**How to Extend:**
```python
from dotfiles_template_renderer.core import TemplateRenderer
from dotfiles_template_renderer.core.types import (
    RenderConfig, TemplateInfo, ValidationResult
)

class MakoRenderer(TemplateRenderer):
    """Mako template renderer implementation."""

    def __init__(self, template_dir, config=None):
        super().__init__(template_dir, config)
        # Initialize Mako-specific components
        from mako.lookup import TemplateLookup
        self._lookup = TemplateLookup(directories=[str(self.template_dir)])

    def render(self, template_name, variables=None, **kwargs):
        all_variables = {**(variables or {}), **kwargs}
        template = self._lookup.get_template(template_name)
        return template.render(**all_variables)

    def validate(self, template_name, variables=None):
        # Implement validation logic
        pass

    def get_template_variables(self, template_name):
        # Implement variable extraction
        pass

    def get_available_templates(self):
        # Implement template discovery
        pass

    def get_template_info(self, template_name):
        # Implement template info
        pass
```

**Extension Points:**
- Subclass TemplateRenderer
- Implement all abstract methods
- Use same type definitions (RenderConfig, ValidationResult, etc.)
- Export from renderers/__init__.py

**2. Custom Validators**

**How to Extend:**
```python
from dotfiles_template_renderer.validators import validate_variables

def validate_variables_with_types(
    template_name: str,
    required_variables: set[str],
    provided_variables: dict[str, Any],
    expected_types: dict[str, type],
    strict: bool = True,
) -> ValidationResult:
    # First, validate presence
    result = validate_variables(template_name, required_variables, provided_variables, strict)

    # Then, validate types
    type_errors = validate_variable_types(provided_variables, expected_types)
    result.errors.extend(type_errors)
    result.is_valid = len(result.errors) == 0

    return result
```

**Extension Points:**
- Add new validation functions to validators.py
- Extend ValidationResult with custom fields
- Create custom validator classes

**3. Custom Filters/Tests/Globals**

**How to Extend:**
```python
# Define custom filters
def markdown_filter(text):
    import markdown
    return markdown.markdown(text)

def slugify_filter(text):
    import re
    return re.sub(r'[^\w\s-]', '', text.lower()).replace(' ', '-')

# Define custom tests
def is_url_test(value):
    import re
    url_pattern = r'^https?://'
    return bool(re.match(url_pattern, value))

# Define custom globals
import datetime

custom_globals = {
    "now": datetime.datetime.now,
    "today": datetime.date.today,
}

# Use in renderer
config = RenderConfig(
    custom_filters={
        "markdown": markdown_filter,
        "slugify": slugify_filter,
    },
    custom_tests={
        "url": is_url_test,
    },
    custom_globals=custom_globals,
)

renderer = Jinja2Renderer("templates", config=config)

# In template:
# {{ content | markdown }}
# {{ title | slugify }}
# {% if link is url %}
# {{ now() }}
```

**Extension Points:**
- Add custom filters via RenderConfig.custom_filters
- Add custom tests via RenderConfig.custom_tests
- Add custom globals via RenderConfig.custom_globals

**4. Custom Exception Types**

**How to Extend:**
```python
from dotfiles_template_renderer.core.exceptions import ValidationError

class TemplateSecurityError(ValidationError):
    """Raised when template contains security issues."""

    def __init__(self, issue: str, template_name: str | None = None):
        self.issue = issue
        message = f"Security issue detected: {issue}"
        super().__init__(message, template_name)

class TemplateDeprecationWarning(ValidationError):
    """Raised when template uses deprecated features."""

    def __init__(self, feature: str, template_name: str | None = None):
        self.feature = feature
        message = f"Deprecated feature used: {feature}"
        super().__init__(message, template_name)
```

**Extension Points:**
- Subclass existing exceptions
- Add to core/exceptions.py
- Export from core/__init__.py

**5. Custom Configuration Options**

**How to Extend:**
```python
from dataclasses import dataclass, field
from dotfiles_template_renderer.core.types import RenderConfig

@dataclass
class ExtendedRenderConfig(RenderConfig):
    """Extended configuration with additional options."""

    enable_caching: bool = True
    cache_size: int = 128
    render_timeout: int = 30
    max_template_size: int = 1024 * 1024
    allowed_extensions: list[str] = field(default_factory=lambda: [".j2", ".jinja", ".jinja2"])
```

**Extension Points:**
- Extend RenderConfig dataclass
- Add new configuration options
- Use in custom renderer implementations

### Future Roadmap

**Potential Enhancements:**

**1. Template Caching Layer**
- Cache rendered results for static content
- Configurable cache backend (memory, Redis, etc.)
- Cache invalidation strategies
- TTL support

**2. Template Preprocessing**
- Minification for production templates
- Syntax validation at load time
- Template linting
- Automatic optimization

**3. Enhanced Validation**
- Type checking for variables
- Schema validation (JSON Schema, Pydantic)
- Required vs. optional variable distinction
- Default value suggestions

**4. Template Metrics**
- Rendering performance metrics
- Template usage statistics
- Variable usage tracking
- Error rate monitoring

**5. Additional Template Engines**
- Mako renderer
- Mustache renderer
- Handlebars renderer
- Custom DSL renderer

**6. Template Testing Framework**
- Unit tests for templates
- Snapshot testing
- Regression testing
- Coverage analysis

**7. Template Documentation Generation**
- Auto-generate docs from templates
- Variable documentation
- Usage examples
- API documentation

**8. IDE Integration**
- VSCode extension for template editing
- Autocomplete for variables
- Syntax highlighting
- Error detection

### Migration Guides

**Migrating from Direct Jinja2 Usage:**

**Before:**
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("app.j2")
result = template.render(name="myapp", version="1.0")
```

**After:**
```python
from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer("templates")
result = renderer.render("app.j2", variables={"name": "myapp", "version": "1.0"})
```

**Benefits:**
- Built-in validation
- Consistent error handling
- Template introspection
- Type safety

**Migrating from String Formatting:**

**Before:**
```python
template = "FROM {base_image}\nLABEL name={name}\n"
result = template.format(base_image="python:3.12", name="myapp")
```

**After:**
```python
# Create template file: templates/app.j2
# FROM {{ base_image }}
# LABEL name={{ name }}

from dotfiles_template_renderer import Jinja2Renderer

renderer = Jinja2Renderer("templates")
result = renderer.render("app.j2", variables={"base_image": "python:3.12", "name": "myapp"})
```

**Benefits:**
- Separation of template from code
- More powerful template syntax
- Validation and error handling
- Reusable templates

**Migrating to Strict Mode:**

**Before (Lenient):**
```python
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=False))
result = renderer.render("app.j2", variables={"name": "myapp"})
# Missing variables use defaults in template
```

**After (Strict):**
```python
renderer = Jinja2Renderer("templates", config=RenderConfig(strict_mode=True))

# Get required variables first
required_vars = renderer.get_template_variables("app.j2")

# Provide all required variables
variables = {var: get_value(var) for var in required_vars}
result = renderer.render("app.j2", variables=variables)
```

**Benefits:**
- Catch missing variables early
- Prevent invalid output
- Better error messages

---

## Code Examples

*Code examples will be added throughout the investigation*

**Target:** 50+ examples

**Current Count:** 0

---

## Architecture Diagrams

*Architecture diagrams will be added throughout the investigation*

**Target:** 5+ diagrams

**Current Count:** 0

---

**End of Investigation Notes**

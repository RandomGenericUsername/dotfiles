"""CLI interface for template renderer using Typer."""

import json
import sys
from pathlib import Path
from typing import Any

import typer
from dotfiles_template_renderer import (
    Jinja2Renderer,
    MissingVariableError,
    RenderConfig,
    TemplateNotFoundError,
    TemplateRenderError,
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Create Typer app
app = typer.Typer(
    name="template-render",
    help="CLI tool for rendering Jinja2 templates with validation",
    add_completion=False,
)

# Rich console for beautiful output
console = Console()


def load_variables_from_file(file_path: Path) -> dict[str, Any]:
    """Load variables from JSON or YAML file."""
    try:
        content = file_path.read_text()

        # Try JSON first
        if file_path.suffix in [".json"]:
            return json.loads(content)

        # Try YAML
        if file_path.suffix in [".yaml", ".yml"]:
            try:
                import yaml

                return yaml.safe_load(content)
            except ImportError:
                console.print(
                    "[red]Error: PyYAML not installed. Install with: pip install pyyaml[/red]"
                )
                sys.exit(1)

        # Default to JSON
        return json.loads(content)

    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON in {file_path}: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(
            f"[red]Error loading variables from {file_path}: {e}[/red]"
        )
        sys.exit(1)


def parse_var_argument(var_str: str) -> tuple[str, Any]:
    """Parse a key=value argument into a tuple."""
    if "=" not in var_str:
        console.print(
            f"[red]Error: Invalid variable format '{var_str}'. Use key=value[/red]"
        )
        sys.exit(1)

    key, value = var_str.split("=", 1)

    # Try to parse value as JSON for complex types
    try:
        parsed_value = json.loads(value)
        return key, parsed_value
    except json.JSONDecodeError:
        # If not valid JSON, treat as string
        return key, value


@app.command(name="render")
def render_command(
    template: str = typer.Argument(
        ...,
        help="Template name (relative to template directory)",
    ),
    template_dir: Path = typer.Option(
        Path(),
        "--template-dir",
        "-d",
        help="Directory containing templates",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    vars_file: Path | None = typer.Option(
        None,
        "--vars-file",
        "-f",
        help="JSON or YAML file containing template variables",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    vars_json: str | None = typer.Option(
        None,
        "--vars-json",
        "-j",
        help="JSON string containing template variables",
    ),
    var: list[str] | None = typer.Option(
        None,
        "--var",
        "-v",
        help="Variable in key=value format (can be specified multiple times)",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: stdout)",
    ),
    strict: bool = typer.Option(
        True,
        "--strict/--no-strict",
        help="Enable strict mode (fail on missing variables)",
    ),
    show_info: bool = typer.Option(
        False,
        "--show-info",
        help="Show template info before rendering",
    ),
):
    """Render a Jinja2 template with provided variables.

    Examples:

        # Render with variables from file
        template-render render app.j2 -d templates/ -f vars.json

        # Render with inline JSON
        template-render render app.j2 -j '{"name": "myapp", "version": "1.0"}'

        # Render with key=value pairs
        template-render render app.j2 -v name=myapp -v version=1.0

        # Combine multiple sources (merged in order: file, json, vars)
        template-render render app.j2 -f base.json -v name=override

        # Save to file
        template-render render app.j2 -f vars.json -o output.txt

        # Disable strict mode
        template-render render app.j2 -f vars.json --no-strict
    """
    try:
        # Create renderer
        config = RenderConfig(strict_mode=strict)
        renderer = Jinja2Renderer(template_dir=template_dir, config=config)

        # Show template info if requested
        if show_info:
            try:
                info = renderer.get_template_info(template)
                console.print(
                    Panel(
                        f"[cyan]Template:[/cyan] {info.name}\n"
                        f"[cyan]Size:[/cyan] {info.size} bytes\n"
                        f"[cyan]Required Variables:[/cyan] {', '.join(info.required_variables) if info.required_variables else 'None'}",
                        title="Template Information",
                        border_style="cyan",
                    )
                )
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not get template info: {e}[/yellow]"
                )

        # Collect variables from all sources
        variables: dict[str, Any] = {}

        # 1. Load from file
        if vars_file:
            variables.update(load_variables_from_file(vars_file))

        # 2. Load from JSON string
        if vars_json:
            try:
                variables.update(json.loads(vars_json))
            except json.JSONDecodeError as e:
                console.print(
                    f"[red]Error: Invalid JSON in --vars-json: {e}[/red]"
                )
                sys.exit(1)

        # 3. Load from key=value pairs
        if var:
            for var_str in var:
                key, value = parse_var_argument(var_str)
                variables[key] = value

        # Render template
        result = renderer.render(template, variables=variables)

        # Output result
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(result)
            console.print(
                f"[green]✓ Template rendered successfully to {output}[/green]"
            )
        else:
            console.print(result)

    except TemplateNotFoundError as e:
        console.print(f"[red]✗ Template not found: {e.template_name}[/red]")
        console.print(f"[yellow]Searched in: {template_dir}[/yellow]")
        sys.exit(1)

    except MissingVariableError as e:
        console.print(
            f"[red]✗ Missing required variables: {', '.join(e.missing_variables)}[/red]"
        )
        console.print(
            "[yellow]Tip: Use --show-info to see required variables[/yellow]"
        )
        console.print(
            "[yellow]Tip: Use --no-strict to allow missing variables[/yellow]"
        )
        sys.exit(1)

    except TemplateRenderError as e:
        console.print(f"[red]✗ Template rendering failed: {e.message}[/red]")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {e}[/red]")
        sys.exit(1)


@app.command(name="list")
def list_command(
    template_dir: Path = typer.Option(
        Path(),
        "--template-dir",
        "-d",
        help="Directory containing templates",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
):
    """List all available templates in the template directory.

    Examples:

        # List templates in current directory
        template-render list

        # List templates in specific directory
        template-render list -d templates/
    """
    try:
        renderer = Jinja2Renderer(template_dir=template_dir)
        templates = renderer.get_available_templates()

        if not templates:
            console.print(
                f"[yellow]No templates found in {template_dir}[/yellow]"
            )
            console.print(
                "[dim]Templates should have .j2, .jinja, or .jinja2 extension[/dim]"
            )
            return

        # Create table
        table = Table(
            title=f"Available Templates in {template_dir}", show_header=True
        )
        table.add_column("Template", style="cyan", no_wrap=True)
        table.add_column("Size", style="green", justify="right")
        table.add_column("Required Variables", style="yellow")

        for template_name in templates:
            try:
                info = renderer.get_template_info(template_name)
                size_kb = info.size / 1024
                size_str = (
                    f"{size_kb:.2f} KB" if size_kb >= 1 else f"{info.size} B"
                )
                vars_str = (
                    ", ".join(info.required_variables)
                    if info.required_variables
                    else "[dim]None[/dim]"
                )
                table.add_row(template_name, size_str, vars_str)
            except Exception:
                table.add_row(template_name, "[dim]?[/dim]", "[dim]?[/dim]")

        console.print(table)
        console.print(f"\n[green]Found {len(templates)} template(s)[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        sys.exit(1)


@app.command(name="info")
def info_command(
    template: str = typer.Argument(
        ...,
        help="Template name",
    ),
    template_dir: Path = typer.Option(
        Path(),
        "--template-dir",
        "-d",
        help="Directory containing templates",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
):
    """Show detailed information about a template.

    Examples:

        # Show info for a template
        template-render info app.j2

        # Show info with custom template directory
        template-render info app.j2 -d templates/
    """
    try:
        renderer = Jinja2Renderer(template_dir=template_dir)
        info = renderer.get_template_info(template)

        # Create info panel
        size_kb = info.size / 1024
        size_str = (
            f"{size_kb:.2f} KB" if size_kb >= 1 else f"{info.size} bytes"
        )

        info_text = f"""[cyan]Name:[/cyan] {info.name}
[cyan]Path:[/cyan] {info.path}
[cyan]Size:[/cyan] {size_str}
[cyan]Required Variables:[/cyan] {len(info.required_variables)}"""

        if info.required_variables:
            info_text += "\n\n[yellow]Variables:[/yellow]"
            for var in info.required_variables:
                info_text += f"\n  • {var}"

        if info.description:
            info_text += f"\n\n[cyan]Description:[/cyan]\n{info.description}"

        console.print(
            Panel(info_text, title="Template Information", border_style="cyan")
        )

    except TemplateNotFoundError as e:
        console.print(f"[red]✗ Template not found: {e.template_name}[/red]")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        sys.exit(1)


@app.command(name="validate")
def validate_command(
    template: str = typer.Argument(
        ...,
        help="Template name",
    ),
    template_dir: Path = typer.Option(
        Path(),
        "--template-dir",
        "-d",
        help="Directory containing templates",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    vars_file: Path | None = typer.Option(
        None,
        "--vars-file",
        "-f",
        help="JSON or YAML file containing template variables",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    vars_json: str | None = typer.Option(
        None,
        "--vars-json",
        "-j",
        help="JSON string containing template variables",
    ),
    var: list[str] | None = typer.Option(
        None,
        "--var",
        "-v",
        help="Variable in key=value format (can be specified multiple times)",
    ),
):
    """Validate that all required variables are provided for a template.

    Examples:

        # Validate with variables from file
        template-render validate app.j2 -f vars.json

        # Validate with inline JSON
        template-render validate app.j2 -j '{"name": "myapp"}'

        # Validate with key=value pairs
        template-render validate app.j2 -v name=myapp -v version=1.0
    """
    try:
        renderer = Jinja2Renderer(template_dir=template_dir)

        # Collect variables from all sources
        variables: dict[str, Any] = {}

        if vars_file:
            variables.update(load_variables_from_file(vars_file))

        if vars_json:
            try:
                variables.update(json.loads(vars_json))
            except json.JSONDecodeError as e:
                console.print(
                    f"[red]Error: Invalid JSON in --vars-json: {e}[/red]"
                )
                sys.exit(1)

        if var:
            for var_str in var:
                key, value = parse_var_argument(var_str)
                variables[key] = value

        # Validate
        validation = renderer.validate(template, variables=variables)

        # Display results
        if validation.is_valid:
            console.print(
                Panel(
                    "[green]✓ Validation passed[/green]\n\n"
                    f"All {len(validation.required_variables)} required variable(s) are provided.",
                    title="Validation Result",
                    border_style="green",
                )
            )

            if validation.unused_variables:
                console.print(
                    f"\n[yellow]Note: {len(validation.unused_variables)} unused variable(s):[/yellow]"
                )
                for var in validation.unused_variables:
                    console.print(f"  • {var}")
        else:
            console.print(
                Panel(
                    "[red]✗ Validation failed[/red]",
                    title="Validation Result",
                    border_style="red",
                )
            )

            if validation.missing_variables:
                console.print(
                    f"\n[red]Missing {len(validation.missing_variables)} required variable(s):[/red]"
                )
                for var in validation.missing_variables:
                    console.print(f"  • {var}")

            if validation.errors:
                console.print("\n[red]Errors:[/red]")
                for error in validation.errors:
                    console.print(f"  • {error}")

            sys.exit(1)

        if validation.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in validation.warnings:
                console.print(f"  • {warning}")

    except TemplateNotFoundError as e:
        console.print(f"[red]✗ Template not found: {e.template_name}[/red]")
        sys.exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        sys.exit(1)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
    ),
):
    """
    Template Renderer CLI - Render Jinja2 templates with validation.

    This tool provides a command-line interface for rendering Jinja2 templates
    with strict variable validation, template introspection, and flexible
    variable input methods.

    Commands:

        render      Render a template with variables
        list        List all available templates
        info        Show detailed template information
        validate    Validate variables against template

    Examples:

        # Render a template
        template-render render app.j2 -f vars.json

        # List available templates
        template-render list -d templates/

        # Show template info
        template-render info app.j2

        # Validate variables
        template-render validate app.j2 -f vars.json
    """
    if version:
        console.print("template-renderer-cli version 0.1.0")
        raise typer.Exit()


if __name__ == "__main__":
    app()

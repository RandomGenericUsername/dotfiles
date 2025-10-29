"""Output manager for writing color schemes to files.

This module provides the OutputManager class that writes ColorScheme objects
to files using Jinja2 templates. This is separate from backends - backends
extract colors, OutputManager writes them to files.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, UndefinedError

from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.config.enums import ColorFormat
from colorscheme_generator.core.exceptions import OutputWriteError, TemplateRenderError
from colorscheme_generator.core.types import ColorScheme


class OutputManager:
    """Manages writing ColorScheme objects to files.
    
    This class is responsible for:
    1. Loading Jinja2 templates
    2. Rendering templates with ColorScheme data
    3. Writing rendered content to files
    
    It's completely independent of backends - it just takes a ColorScheme
    object and writes it to files in various formats.
    
    Attributes:
        settings: Application configuration
        template_env: Jinja2 environment for template rendering
    
    Example:
        >>> from colorscheme_generator.config.settings import Settings
        >>> manager = OutputManager(Settings.get())
        >>> output_files = manager.write_outputs(
        ...     scheme=color_scheme,
        ...     output_dir=Path("~/.cache/colorscheme"),
        ...     formats=[ColorFormat.JSON, ColorFormat.CSS]
        ... )
    """

    def __init__(self, settings: AppConfig):
        """Initialize OutputManager.
        
        Args:
            settings: Application configuration
        """
        self.settings = settings
        
        # Set up Jinja2 environment
        template_dir = settings.templates.directory
        if not template_dir.is_absolute():
            # Relative to module root
            module_root = Path(__file__).parent.parent.parent.parent
            template_dir = module_root / template_dir
        
        self.template_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined="strict" if settings.templates.strict_mode else "default",
        )

    def write_outputs(
        self,
        scheme: ColorScheme,
        output_dir: Path,
        formats: list[ColorFormat],
    ) -> dict[str, Path]:
        """Write ColorScheme to files in specified formats.
        
        Args:
            scheme: ColorScheme object to write
            output_dir: Directory to write files to
            formats: List of output formats to generate
            
        Returns:
            Dictionary mapping format name to output file path
            
        Raises:
            TemplateRenderError: If template rendering fails
            OutputWriteError: If writing file fails
            
        Example:
            >>> output_files = manager.write_outputs(
            ...     scheme=color_scheme,
            ...     output_dir=Path("~/.cache/colorscheme"),
            ...     formats=[ColorFormat.JSON, ColorFormat.CSS]
            ... )
            >>> print(output_files)
            {
                'json': PosixPath('/home/user/.cache/colorscheme/colors.json'),
                'css': PosixPath('/home/user/.cache/colorscheme/colors.css')
            }
        """
        # Ensure output directory exists
        output_dir = output_dir.expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        output_files = {}

        for fmt in formats:
            try:
                # Render template
                content = self._render_template(scheme, fmt)
                
                # Write to file
                output_path = output_dir / f"colors.{fmt.value}"
                self._write_file(output_path, content)
                
                output_files[fmt.value] = output_path
                
            except (TemplateRenderError, OutputWriteError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Wrap unexpected errors
                raise OutputWriteError(
                    str(output_dir / f"colors.{fmt.value}"),
                    f"Unexpected error: {e}"
                )

        return output_files

    def _render_template(self, scheme: ColorScheme, fmt: ColorFormat) -> str:
        """Render template for given format.
        
        Args:
            scheme: ColorScheme object
            fmt: Output format
            
        Returns:
            Rendered template content
            
        Raises:
            TemplateRenderError: If rendering fails
        """
        template_name = f"colors.{fmt.value}.j2"
        
        try:
            template = self.template_env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateRenderError(
                template_name,
                f"Template not found in {self.settings.templates.directory}"
            )
        
        # Prepare template context
        context = {
            "background": scheme.background,
            "foreground": scheme.foreground,
            "cursor": scheme.cursor,
            "colors": scheme.colors,
            "source_image": str(scheme.source_image),
            "backend": scheme.backend,
            "generated_at": scheme.generated_at.isoformat(),
        }
        
        try:
            return template.render(**context)
        except UndefinedError as e:
            raise TemplateRenderError(template_name, f"Undefined variable: {e}")
        except Exception as e:
            raise TemplateRenderError(template_name, str(e))

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to file.
        
        Args:
            path: File path
            content: Content to write
            
        Raises:
            OutputWriteError: If writing fails
        """
        try:
            path.write_text(content)
        except PermissionError:
            raise OutputWriteError(str(path), "Permission denied")
        except OSError as e:
            raise OutputWriteError(str(path), str(e))


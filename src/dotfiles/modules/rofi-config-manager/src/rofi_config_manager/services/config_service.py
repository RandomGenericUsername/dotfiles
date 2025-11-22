"""Service for generating rofi configurations."""

from pathlib import Path

from dotfiles_template_renderer import Jinja2Renderer

from rofi_config_manager.client.manager_client import ManagerClient
from rofi_config_manager.config.config import AppConfig
from rofi_config_manager.config.types import RofiConfigType
from rofi_config_manager.models.render_context import RofiRenderContext


class RofiConfigService:
    """Service for generating rofi configurations."""

    def __init__(self, config: AppConfig):
        """Initialize service.

        Args:
            config: Application configuration
        """
        self.config = config
        self.manager_client = ManagerClient(config.paths.dotfiles_manager_path)
        self.renderer = Jinja2Renderer(config.paths.templates_dir)

    def generate_all_configs(self) -> dict[str, Path]:
        """Generate all enabled rofi configurations.

        Returns:
            Dict mapping config type to output path
        """
        results = {}
        for config_type in RofiConfigType:
            if self.config.configs.get(config_type.value, True):
                output_path = self.generate_config(config_type)
                results[config_type.value] = output_path
        return results

    def generate_config(self, config_type: RofiConfigType) -> Path:
        """Generate a specific rofi configuration.

        Args:
            config_type: Type of config to generate

        Returns:
            Path to generated config file
        """
        # Build render context from manager state + config schema
        context = self._build_render_context(config_type)

        # Generate wrapper scripts for modi (if any)
        if context.modi.has_modi:
            self._generate_modi_wrappers(context.modi, config_type)

        # Render template
        template_vars = context.to_template_dict()
        output_path = (
            self.config.paths.output_dir / config_type.output_filename
        )

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.renderer.render_to_file(
            config_type.template_name,
            output_path,
            variables=template_vars,
        )

        return output_path

    def _generate_modi_wrappers(
        self, modi_config, config_type: RofiConfigType
    ) -> None:
        """Generate wrapper scripts for modi.

        Rofi cannot execute scripts with arguments directly, so we create
        wrapper scripts that call the actual command with arguments.

        Args:
            modi_config: Modi configuration
            config_type: Type of config being generated
        """
        scripts_dir = self.config.paths.output_dir / ".scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        for modi in modi_config.modi_list:
            # Create wrapper script name
            wrapper_name = f"{config_type.value}-{modi.name}"
            wrapper_path = scripts_dir / wrapper_name

            # Generate wrapper script content
            wrapper_content = f"""#!/bin/sh
# Auto-generated wrapper for rofi modi: {modi.name}
# DO NOT EDIT MANUALLY
exec {modi.script} "$@"
"""

            # Write wrapper script
            wrapper_path.write_text(wrapper_content)
            wrapper_path.chmod(0o755)  # Make executable

            # Update modi script to point to wrapper
            modi.script = str(wrapper_path)

    def _build_render_context(
        self, config_type: RofiConfigType
    ) -> RofiRenderContext:
        """Build render context from manager state and config schema.

        Args:
            config_type: Type of config being generated

        Returns:
            Render context with system state and config schema
        """
        # Get config schema (defines structure)
        schema = config_type.schema

        # Query manager for system state
        sys_attrs = self.manager_client.get_system_attributes()
        colorscheme = self.manager_client.get_current_colorscheme()
        wallpaper = self.manager_client.get_current_wallpaper()

        # Get border width (with per-config override support)
        border_width = self.config.styling.get_border_width(config_type.value)

        # Get modi configuration from settings (overrides schema defaults)
        modi_config = self.config.get_modi_config(config_type.value)

        # If no user-configured modi, use schema defaults
        if not modi_config.has_modi and schema.modi.has_modi:
            modi_config = schema.modi

        # Extract colors from colorscheme JSON
        colors = []
        for i in range(16):
            colors.append(colorscheme["colors"][f"color{i}"])

        return RofiRenderContext(
            # System attributes
            font_family=sys_attrs["font_family"],
            font_size=sys_attrs["font_size"],
            border_width=border_width,
            # Colors
            background=colorscheme["special"]["background"],
            foreground=colorscheme["special"]["foreground"],
            cursor=colorscheme["special"]["cursor"],
            colors=colors,
            # Wallpaper
            current_wallpaper=wallpaper,
            # Modi (from settings or schema)
            modi=modi_config,
            # Configuration block (from schema)
            sidebar_mode=schema.sidebar_mode,
            click_to_exit=schema.click_to_exit,
            show_icons=schema.show_icons,
            scroll_method=schema.scroll_method,
        )

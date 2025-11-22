"""Rofi configuration hook."""

import subprocess
from pathlib import Path

from dotfiles_manager.hooks.base import Hook
from dotfiles_manager.models.hook import HookContext, HookResult


class RofiConfigHook(Hook):
    """Hook to regenerate rofi configurations after wallpaper change."""

    def __init__(self, rofi_config_manager_path: Path):
        """Initialize rofi config hook.

        Args:
            rofi_config_manager_path: Path to rofi-config-manager CLI
        """
        self._rofi_config_manager_path = rofi_config_manager_path

    @property
    def name(self) -> str:
        """Unique identifier for this hook."""
        return "rofi_config"

    def execute(self, context: HookContext) -> HookResult:
        """Execute hook to regenerate rofi configurations.

        Args:
            context: Hook execution context

        Returns:
            HookResult: Result of hook execution
        """
        try:
            # Skip if colorscheme was not generated
            if not context.colorscheme_generated:
                return HookResult(
                    success=True,
                    message="Skipped (no colorscheme generated)",
                )

            # Call rofi-config-manager to regenerate all configs
            result = subprocess.run(
                [str(self._rofi_config_manager_path), "generate", "--all"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse output to count generated configs
            # Output format: "✓ Generated N config(s)"
            output = result.stdout.strip()
            if "Generated" in output:
                # Extract count from output
                parts = output.split("Generated")
                if len(parts) > 1:
                    count_part = parts[1].strip().split()[0]
                    message = f"Generated {count_part} rofi config(s)"
                else:
                    message = "Generated rofi configs"
            else:
                message = "Generated rofi configs"

            return HookResult(
                success=True,
                message=message,
            )

        except subprocess.CalledProcessError as e:
            return HookResult(
                success=False,
                message=f"Failed to generate rofi configs: {e.stderr}",
            )
        except Exception as e:
            return HookResult(
                success=False,
                message=f"Failed to generate rofi configs: {e}",
            )

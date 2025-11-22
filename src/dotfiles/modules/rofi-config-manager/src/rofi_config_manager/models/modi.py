"""Modi models for rofi configuration."""

from pydantic import BaseModel, Field


class RofiModi(BaseModel):
    """Represents a single rofi modi."""

    name: str = Field(
        ..., description="Modi display name (e.g., 'wallpapers')"
    )
    script: str = Field(
        ...,
        description="Script/command to execute (e.g., 'rofi-wallpaper-selector wallpapers')",
    )

    def to_modi_string(self) -> str:
        """Convert to rofi modi format: 'name:script'.

        Returns:
            Modi string in rofi format
        """
        # Rofi expects the script path and arguments as a single string
        # It will execute it directly, so no shell escaping needed
        return f"{self.name}:{self.script}"


class ModiConfig(BaseModel):
    """Configuration for rofi modi."""

    enabled: bool = Field(
        default=False, description="Whether this config uses modi"
    )
    modi_list: list[RofiModi] = Field(
        default_factory=list, description="List of modi"
    )

    def to_rofi_config_string(self) -> str:
        """Convert to rofi configuration string.

        Returns:
            Comma-separated modi string: "name1:script1,name2:script2"
        """
        if not self.enabled or not self.modi_list:
            return ""
        return ",".join(modi.to_modi_string() for modi in self.modi_list)

    @property
    def has_modi(self) -> bool:
        """Check if modi are configured.

        Returns:
            True if modi are enabled and list is not empty
        """
        return self.enabled and len(self.modi_list) > 0

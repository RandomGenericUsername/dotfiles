"""System attributes model."""

from pydantic import BaseModel, Field


class SystemAttributes(BaseModel):
    """System-wide attributes managed by dotfiles manager.

    Attributes:
        font_family: System font family (e.g., "JetBrains Mono")
        font_size: System font size in pixels
        monitors: List of monitor names (e.g., ["DP-1", "HDMI-1"])
    """

    font_family: str = Field(
        default="JetBrains Mono",
        description="System font family",
    )
    font_size: int = Field(
        default=14,
        ge=8,
        le=72,
        description="System font size in pixels",
    )
    monitors: list[str] = Field(
        default_factory=list,
        description="List of monitor names (empty = auto-detect)",
    )

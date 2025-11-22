"""Configuration for rofi-config-manager."""

from rofi_config_manager.config.config import AppConfig, load_config
from rofi_config_manager.config.types import ConfigSchema, RofiConfigType

__all__ = ["AppConfig", "load_config", "RofiConfigType", "ConfigSchema"]

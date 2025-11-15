"""Hook system for dotfiles manager."""

from dotfiles_manager.hooks.base import Hook
from dotfiles_manager.hooks.registry import HookRegistry
from dotfiles_manager.hooks.wlogout_hook import WlogoutIconsHook

__all__ = [
    "Hook",
    "HookRegistry",
    "WlogoutIconsHook",
]

"""Application-specific exceptions for the dotfiles installer."""


class InstallationConfirmationDeclinedException(Exception):
    """Exception raised when user declines installation."""

    pass

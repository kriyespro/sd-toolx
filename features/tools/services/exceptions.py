"""Tool processing exceptions."""


class ToolError(Exception):
    """Base tool error with user-facing message."""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class UpgradeRequired(ToolError):
    """Free tier limit reached."""


class FileValidationError(ToolError):
    """Invalid upload."""

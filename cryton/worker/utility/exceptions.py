class Error(Exception):
    """Base class for exceptions in this module."""


class ListenerError(Error):
    """Base class for Listener exceptions."""


class ListenerTypeDoesNotExist(ListenerError):
    """Exception raised when Listener type doesn't match existing types."""

    def __init__(self, trigger_type: str, existing_triggers: list):
        self.message = (
            f"Nonexistent Listener type '{trigger_type}'. "
            f"Supported Listener types are: {', '.join(existing_triggers)}."
        )
        super().__init__(self.message)


class TooManyTriggers(ListenerError):
    """Exception raised when Listener can't contain more triggers."""

    def __init__(self, trigger_type: str):
        self.message = f"Listener '{trigger_type}' can't contain more triggers."
        super().__init__(self.message)

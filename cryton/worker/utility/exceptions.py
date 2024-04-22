class Error(Exception):
    """Base class for exceptions in this module."""


class ListenerError(Error):
    """Base class for Listener exceptions."""


class MsfError(Error):
    """Base class for MSF exceptions."""


class MsfConnectionError(MsfError):
    """Exception raised when connection to MSF RPC server cannot be established"""

    def __init__(self):
        self.message = f"Cannot connect to MSF RPC server"
        super().__init__(self.message)


class MsfSessionNotFound(MsfError):
    """Exception raised when Session ID was not found in MSF."""

    def __init__(self, session_id: str):
        self.message = f"Session '{session_id}' not found in MSF."
        super().__init__(self.message)


class MsfModuleNotFound(MsfError):
    """Exception raised when Module was not found in MSF."""

    def __init__(self, module_name: str):
        self.message = f"Module '{module_name}' not found in MSF."
        super().__init__(self.message)


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

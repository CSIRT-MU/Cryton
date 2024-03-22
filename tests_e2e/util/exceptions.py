class Error(Exception):
    """Base class for exceptions in this module."""


class CannotParseResponseError(Error):
    """Raised when cannot parse a response from an executed command."""


class UnexpectedResponse(Error):
    """Raised when got an unexpected response."""


class TimeOutError(Error):
    """Raised when an action timeout occurred."""

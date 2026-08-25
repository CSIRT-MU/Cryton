from enum import StrEnum, auto


class Result(StrEnum):
    """
    Module result options.
    """

    OK = auto()
    FAIL = auto()
    ERROR = auto()
    STOPPED = auto()

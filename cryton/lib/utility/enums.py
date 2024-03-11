from enum import Enum, EnumMeta


class EnumMetaSearchable(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class StrEnum(str, Enum, metaclass=EnumMetaSearchable):
    @classmethod
    def values(cls) -> list:
        return [x.value for x in cls]


class Result(StrEnum):  # StrEnum + auto() introduced in Py3.11
    """
    Module result options.
    """
    OK = "ok"
    FAIL = "fail"
    ERROR = "error"
    TERMINATED = "terminated"
    UNKNOWN = "unknown"

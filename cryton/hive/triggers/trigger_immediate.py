from datetime import datetime

from cryton.hive.triggers.abstract import Trigger


class TriggerImmediate(Trigger):
    """
    Trigger the stage immediately.
    """

    @classmethod
    def start(cls, **kwargs) -> tuple[str, datetime | None]:
        return "", None

    @classmethod
    def stop(cls, **kwargs) -> None:
        pass

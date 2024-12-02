from abc import ABC, abstractmethod
from datetime import datetime


class Trigger(ABC):
    """
    Trigger abstract.
    """

    @classmethod
    @abstractmethod
    def start(cls, **kwargs) -> tuple[str, datetime | None]:
        """
        Start the trigger.
        :param kwargs: Arguments used for starting the trigger.
        :return: trigger ID and its scheduled time
        """

    @classmethod
    @abstractmethod
    def stop(cls, **kwargs) -> None:
        """
        Stop the trigger.
        :param kwargs: Arguments used for stopping the trigger.
        :return: None
        """

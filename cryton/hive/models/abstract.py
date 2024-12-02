from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class Instance(ABC):
    @abstractmethod
    def __init__(self, model_id: int):
        pass

    @staticmethod
    @abstractmethod
    def create_model(**kwargs):
        pass


class Execution(Instance, ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def finish(self) -> None:
        pass

    @abstractmethod
    def report(self) -> dict:
        pass


class SchedulableExecution(Execution, ABC):
    @abstractmethod
    def schedule(self, schedule_time: datetime) -> None:
        pass

    @abstractmethod
    def unschedule(self) -> None:
        pass

    @abstractmethod
    def reschedule(self, schedule_time: datetime) -> None:
        pass

    @abstractmethod
    def pause(self) -> None:
        pass

    @abstractmethod
    def resume(self) -> None:
        pass

    @abstractmethod
    def validate_modules(self) -> None:
        pass

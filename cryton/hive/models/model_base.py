from abc import ABC, abstractmethod


class ModelBase(ABC):
    @classmethod
    @abstractmethod
    def validate(cls):
        pass

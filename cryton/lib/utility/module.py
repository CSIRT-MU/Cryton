from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from copy import deepcopy
from jsonschema import validate

from cryton.lib.utility.enums import Result


@dataclass
class ModuleOutput:
    """
    Standardized module output.
    """
    result: Result = Result.FAIL
    output: str = ""
    serialized_output: dict = field(default_factory=dict)


class ModuleBase(ABC):
    SCHEMA = {}

    def __init__(self, arguments: dict):
        """
        Base class used for module creation. It contains the basic structure that must be implemented in a module.
        :param arguments: Arguments to influence the execution
        """
        self._data = ModuleOutput()
        self._arguments = deepcopy(arguments)

    @classmethod
    def validate_arguments(cls, arguments: dict) -> None:
        """
        Validate input arguments using jsonschema.
        :param arguments: Module arguments
        :return: None
        :exception Exception: In case of error
        """
        validate(arguments, cls.SCHEMA)

    @abstractmethod
    def check_requirements(self) -> None:
        """
        Check for system requirements, like executable, connection to Metasploit/Empire, and other.
        :return: None
        :exception Exception: In case of error
        """

    @abstractmethod
    def execute(self) -> ModuleOutput:
        """
        Entry point used for module execution. Any code you want to execute must be called from here.
        :return: Standardized module output
        """

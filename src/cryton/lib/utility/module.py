from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from copy import deepcopy
from jsonschema import validate

from cryton.lib.utility.enums import Result
from cryton.lib.utility.schemas import inject_schema


@dataclass
class ModuleOutput:
    """
    Standardized module output.
    """

    result: Result = Result.FAIL
    output: str = ""
    serialized_output: dict = field(default_factory=dict)


class ModuleBase(ABC):
    _SCHEMA = {}

    def __init__(self, arguments: dict):
        """
        Base class used for module creation. It contains the basic structure that must be implemented in a module.
        :param arguments: Arguments to influence the execution
        """
        self._data = ModuleOutput()
        self._arguments = deepcopy(arguments)

    @classmethod
    def get_schema(cls) -> dict:
        return deepcopy(cls._SCHEMA)

    @classmethod
    def validate_arguments(cls, arguments: dict, allow_unresolved_variables: bool = False) -> None:
        """
        Validate input arguments using jsonschema.
        :param arguments: Module arguments
        :param allow_unresolved_variables: Allow unresolved execution and output sharing variables
        :return: None
        :exception Exception: In case of error
        """
        schema_copy = cls.get_schema()
        schema = inject_schema(schema_copy) if allow_unresolved_variables else schema_copy
        validate(arguments, schema)

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

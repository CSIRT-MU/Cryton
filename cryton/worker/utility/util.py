from types import ModuleType
from importlib import import_module
from pkgutil import iter_modules
import traceback
import time
from dataclasses import dataclass, field

from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


def run_module(name: str, arguments: dict, validate_only: bool = False) -> ModuleOutput:
    """
    Validate arguments and requirements, and execute module with supplied arguments.
    :param name: Module name
    :param arguments: Arguments passed to the module
    :param validate_only: Do not execute the module
    :return: Standardized module output
    """
    # TODO: if the module ends successfully and there is a serialized output, add drop_output flag to drop output
    try:
        module_type = get_module(name)
    except KeyError:
        return ModuleOutput(Result.ERROR, output=f"Module {name} doesn't exist.")

    try:
        module_type.validate_arguments(arguments)
    except Exception as ex:
        return ModuleOutput(Result.FAIL, output=str(ex))

    try:
        module = module_type(arguments)
    except Exception as ex:
        return ModuleOutput(Result.ERROR, str(ex), {"ex_type": str(ex.__class__), "traceback": traceback.format_exc()})

    try:
        module.check_requirements()
    except Exception as ex:
        return ModuleOutput(Result.FAIL, output=str(ex))

    if validate_only:
        return ModuleOutput(Result.OK)

    try:
        return module.execute()
    except Exception as ex:
        return ModuleOutput(Result.ERROR, str(ex), {"ex_type": str(ex.__class__), "traceback": traceback.format_exc()})


def get_module(name: str) -> type[ModuleBase]:
    """
    Filter available modules and get matching module.
    :param name: Module name
    :return: Module class implementation
    """
    available_modules = get_available_modules()
    return available_modules[f"cryton.modules.{name}"].Module


def get_available_modules() -> dict[str, ModuleType]:
    """
    Get list of available modules.
    :return: Available modules
    """
    modules_namespace = import_module("cryton.modules")
    return {
        name: import_module(f"{name}.module")
        for finder, name, ispkg in iter_modules(modules_namespace.__path__, f"{modules_namespace.__name__}.")
    }


@dataclass(order=True)
class PrioritizedItem:
    """
    Item used for ManagerPriorityQueue.
    Priority parameter decides which item (PrioritizedItem) will be processed first.
    Timestamp parameter makes sure the order of processed items (PrioritizedItems) is preserved (AKA FIFO).
    Item parameter stores the process defining value.
    """

    priority: int
    item: dict = field(compare=False)
    timestamp: int = time.time_ns()


@dataclass
class UndeliveredMessage:
    recipient: str
    body: str
    properties: dict

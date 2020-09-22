from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type
    from types import ModuleType

import importlib
import sys
from pathlib import Path
from pyrunner import tasks
from ..tasks.base import Task


def import_module(path: str) -> ModuleType:
    """
    Imports a module by file path.
    :param path: Path to the code file.
    :return: Module object.
    """
    path = Path(path)
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# def load_task(path: str, class_name: str) -> Type[Task]:
#     """
#     Loads a task class from file.
#     :param path: Path to the code file.
#     :param class_name: Name of the task class in the file.
#     :return: Class object of the task.
#     """
#     module = import_module(path)
#     cls = getattr(module, class_name)
#     if not issubclass(cls, Task):
#         raise TypeError("Class {} from file {} is not a task.".format(class_name, path))
#
#     return cls


def load_task(class_name: str, reload: bool = False) -> Type[Task]:
    """
    Returns the class of a task by class name.
    :param class_name: The name of the task class.
    :param reload: Whether to reload the code from disk.
    :return: Class object of the task.
    """
    cls = getattr(tasks, class_name)

    if reload:
        module = importlib.reload(sys.modules[cls.__module__])
        cls = getattr(module, class_name)

    if not issubclass(cls, Task):
        raise TypeError("Class {} is not a task.".format(class_name))

    return cls
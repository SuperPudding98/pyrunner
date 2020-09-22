import importlib
from pathlib import Path
from types import ModuleType
from typing import Type

from ..tasks.base import Task


def import_module(path: str) -> ModuleType:
    """
    Imports a module by file path.
    :param path: Path to the code file.
    :return: Module object.
    """
    path = Path(path)
    spec = importlib.util.spec_from_file(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def load_task(path: str, class_name: str) -> Type[Task]:
    """
    Loads a task class from file.
    :param path: Path to the code file.
    :param class_name: Name of the task class in the file.
    :return: Class object of the task.
    """
    module = import_module(path)
    cls = getattr(module, class_name)
    if not issubclass(cls, Task):
        raise TypeError("Class {} from file {} is not a task.".format(class_name, path))

    return cls

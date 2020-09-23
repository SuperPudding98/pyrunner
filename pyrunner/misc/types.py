from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type
    from collections.abc import Iterable, Mapping
    from pyrunner.tasks.base import Task

from dataclasses import dataclass
from frozendict import frozendict


@dataclass
class TaskMetadata:
    """
    Runner metadata about task.
    """
    name: str
    interval: float
    task_type: Type[Task]
    setup_args: Iterable = ()
    setup_kwargs: Mapping = frozendict()
    teardown_args: Iterable = ()
    teardown_kwargs: Mapping = frozendict()
    execute_args: Iterable = ()
    execute_kwargs: Mapping = frozendict()

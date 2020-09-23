from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from logbook import Logger

from abc import ABC, abstractmethod
from pyrunner.misc.exceptions import TaskAlreadyExistsError, NoSuchTaskError
from pyrunner.misc.types import TaskMetadata


class Runner(ABC):
    """
    An abstract base task runner meant to be extended.
    """
    def __init__(self, logger: Logger):
        """
        Initializes a runner object.
        :param logger: a logbook.Logger the runner will use.
        """
        self.logger = logger
        self.task_data = {}
        self._tasks = {}
        self._running = False

    def _init_task(self, metadata):
        task_logger = type(self.logger)(name=metadata.name)
        task_logger.handlers = self.logger.handlers
        task = metadata.task_type(runner=self, logger=task_logger)

        return task

    @abstractmethod
    def _start_task(self, name):
        task = self._tasks[name]
        metadata = self.task_data[name]
        self.logger.info("Task {} of type {} started running.".format(name, metadata.task_type.__name__))
        task.setup(*metadata.setup_args, **metadata.setup_kwargs)

    @abstractmethod
    def _stop_task(self, name):
        task = self._tasks[name]
        metadata = self.task_data[name]
        task.teardown(*metadata.teardown_args, **metadata.teardown_kwargs)
        self.logger.info("Task {} of type {} finished running.".format(name, metadata.task_type.__name__))

    def add_task(self, task_metadata: TaskMetadata):
        """
        Registers a new task to be run when start method is called.
        :param task_metadata: A TaskMetadata object.
        """
        if task_metadata.name in self.task_data:
            raise TaskAlreadyExistsError("A task named {} is already registered to this runner.".format(task_metadata.name))

        self.task_data[task_metadata.name] = task_metadata
        self._tasks[task_metadata.name] = self._init_task(task_metadata)
        self.logger.info("Task {} of type {} added.".format(task_metadata.name, task_metadata.task_type.__name__))

        if self._running:
            self._start_task(task_metadata.name)

    def remove_task(self, name: str):
        """
        Unregisters a task from the runner.
        If the runner was started, the task teardown will be called.
        :param name: Unique name for the task instance.
        """
        if name not in self.task_data:
            raise NoSuchTaskError("This runner has no task named {}. Cannot remove.".format(name))

        if self._running:
            self._stop_task(name)

        metadata = self.task_data.pop(name)
        self._tasks.pop(name)
        self.logger.info("Task {} of type {} removed.".format(name, metadata.task_type.__name__))

    def start(self):
        """
        Starts the runner. Runs setup of all registered tasks and then executes them periodically.
        """
        self._running = True
        for task_name in self.task_data:
            self._start_task(task_name)

    def stop(self):
        """
        Stops the runner. Runs teardown for all registered tasks.
        """
        for task_name in self.task_data:
            self._stop_task(task_name)
        self._running = False

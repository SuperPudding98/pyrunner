from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from logbook import Logger
    from collections.abc import Iterable, Mapping

from abc import ABC, abstractmethod
from pyrunner.misc.exceptions import TaskAlreadyExistsError, NoSuchTaskError
from pyrunner.misc.types import TaskMetadata
from pyrunner.misc.utils import load_task


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
        self._running = False

    @staticmethod
    def __get_args_kwargs(args, kwargs):
        args = () if args is None else args
        kwargs = {} if kwargs is None else kwargs
        return args, kwargs

    def _create_task_metadata(self, name: str, interval: float, class_name: str, force_reload: bool = False,
                              setup_args: Iterable = None, setup_kwargs: Mapping = None,
                              teardown_args: Iterable = None, teardown_kwargs: Mapping = None,
                              execute_args: Iterable = None, execute_kwargs: Mapping = None) -> TaskMetadata:
        setup_args, setup_kwargs = self.__get_args_kwargs(setup_args, setup_kwargs)
        teardown_args, teardown_kwargs = self.__get_args_kwargs(teardown_args, teardown_kwargs)
        execute_args, execute_kwargs = self.__get_args_kwargs(execute_args, execute_kwargs)

        task_class = load_task(class_name, force_reload)
        task_logger = type(self.logger)(name=name)
        task_logger.handlers = self.logger.handlers
        task = task_class(runner=self, logger=task_logger)

        return TaskMetadata(name, task, interval, class_name,
                                setup_args, setup_kwargs, teardown_args, teardown_kwargs, execute_args, execute_kwargs)

    @abstractmethod
    def _start_task(self, name):
        metadata = self.task_data[name]
        self.logger.info("Task {} of type {} started running.".format(name, metadata.class_name))
        metadata.task.setup(*metadata.setup_args, **metadata.setup_kwargs)

    @abstractmethod
    def _stop_task(self, name):
        metadata = self.task_data[name]
        metadata.task.teardown(*metadata.teardown_args, **metadata.teardown_kwargs)
        self.logger.info("Task {} of type {} finished running.".format(name, metadata.class_name))

    def add_task(self, name: str, interval: float, class_name: str, force_reload: bool = False,
                 setup_args: Iterable = None, setup_kwargs: Mapping = None,
                 teardown_args: Iterable = None, teardown_kwargs: Mapping = None,
                 execute_args: Iterable = None, execute_kwargs: Mapping = None):
        """
        Registers a new task to be run when start method is called.
        If the runner was already started the task will start running immediately.
        :param name: Unique name for the task instance.
        :param interval: Interval in seconds between task executions.
        :param class_name: Name of the task class.
        :param force_reload: Whether to reload the task from the code file on disk.
        :param setup_args: Positional arguments to pass to task setup method.
        :param setup_kwargs: Keyword arguments to pass to task setup method.
        :param teardown_args: Positional arguments to pass to task teardown method.
        :param teardown_kwargs: Keyword arguments to pass to task teardown method.
        :param execute_args: Positional arguments to pass to task execute method.
        :param execute_kwargs: Keyword arguments to pass to task execute method.
        """
        if name in self.task_data:
            raise TaskAlreadyExistsError("A task named {} is already registered to this runner.".format(name))

        metadata = self._create_task_metadata(name, interval, class_name, force_reload,
                                              setup_args, setup_kwargs, teardown_args, teardown_kwargs, execute_args, execute_kwargs)
        self.task_data[name] = metadata
        self.logger.info("Task {} of type {} added.".format(name, metadata.class_name))

        if self._running:
            self._start_task(name)

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
        self.logger.info("Task {} of type {} removed.".format(name, metadata.class_name))

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

from abc import ABC, abstractmethod
from logbook import Logger

from ..runners.base import Runner


class Task(ABC):
    """
    An abstract base class for a scheduled task.
    """
    def __init__(self, runner: Runner, logger: Logger):
        """
        Initializes a new task.
        :param runner: The runner in charge of scheduling the task. The task keeps a reference to the runner to allow tasks to modify tasks.
        :param logger: A logbook.Logger the task will use.
        """
        self.runner = runner
        self.logger = logger

    def setup(self, *args, **kwargs):
        """
        Method that runs once when the task starts running. By default does nothing.
        """
        pass

    def teardown(self, *args, **kwargs):
        """
        Method that runs once when the task finishes running. By default does nothing.
        """
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Method that runs periodically each time the task is executed.
        """
        raise NotImplementedError()

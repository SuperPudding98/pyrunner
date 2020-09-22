from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from logbook import Logger

from threading import Thread, Event
from .base import Runner


class SimpleThreadRunner(Runner):
    """
    A simple runner using a separate thread for each task.
    """
    def __init__(self, logger: Logger):
        """
        Initializes a runner object.
        :param logger: a logbook.Logger the runner will use.
        """
        super().__init__(logger)
        self._threads = {}
        self._kill_events = {}

    def _task_loop(self, name):
        metadata = self.task_data[name]
        self.logger.info("Task {} of type {} started running.".format(name, metadata.class_name))
        metadata.task.setup(*metadata.setup_args, **metadata.setup_kwargs)

        try:
            metadata.task.execute(*metadata.execute_args, **metadata.execute_kwargs)
            while not self._kill_events[name].wait(metadata.interval):
                metadata.task.execute(*metadata.execute_args, **metadata.execute_kwargs)
        finally:
            metadata.task.teardown(*metadata.teardown_args, **metadata.teardown_kwargs)
            self.logger.info("Task {} of type {} finished running.".format(name, metadata.class_name))

    def _start_task(self, name):
        self._kill_events[name] = Event()
        thread = Thread(name=name, target=self._task_loop, args=(name,))
        self._threads[name] = thread

        thread.start()

    def _stop_task(self, name):
        self._kill_events[name].set()

    def stop(self):
        """
        Stops the runner. Runs teardown for all registered tasks.
        """
        super().stop()
        for thread in self._threads.values():
            thread.join()

        self._threads = {}
        self._kill_events = {}

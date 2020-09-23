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

    def _safe_run(self, func, args, kwargs, error_msg="", reraise=True):
        try:
            func(*args, **kwargs)
        except Exception:
            self.logger.exception(error_msg)
            if reraise:
                raise

    def _task_loop(self, name):
        task = self._tasks[name]
        metadata = self.task_data[name]
        self.logger.info("Task {} of type {} started running.".format(name, metadata.task_type.__name__))
        self._safe_run(func=task.setup, args=metadata.setup_args, kwargs=metadata.setup_kwargs,
                       error_msg="Task {} of type {} raised an unhandled exception during setup:".format(name, metadata.task_type.__name__))

        try:
            self._safe_run(func=task.execute, args=metadata.execute_args, kwargs=metadata.execute_kwargs,
                           error_msg="Task {} of type {} raised an unhandled exception during execution:".format(name, metadata.task_type.__name__),
                           reraise=False)
            while not self._kill_events[name].wait(metadata.interval):
                self._safe_run(func=task.execute, args=metadata.execute_args, kwargs=metadata.execute_kwargs,
                               error_msg="Task {} of type {} raised an unhandled exception during execution:".format(name, metadata.task_type.__name__),
                               reraise=False)
        finally:
            self._safe_run(func=task.teardown, args=metadata.teardown_args, kwargs=metadata.teardown_kwargs,
                           error_msg="Task {} of type {} raised an unhandled exception during teardown:".format(name, metadata.task_type.__name__))
            self.logger.info("Task {} of type {} finished running.".format(name, metadata.task_type.__name__))

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

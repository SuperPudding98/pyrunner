import sys
import importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ..base import Task
from .watch_metadata import WatchMetadata


class TaskReloaderTask(Task):
    """
    This task monitors the source code files of all tasks registered to the runner.
    If a file is modified it is reloaded on next execution, all tasks in the file are removed and added again to the runner with the new code.
    Key features:
        - Can reload its own code
        - Can handle multiple tasks in the same file
        - Can handle tasks being added/removed from runner between executions.
    NOTE: Only the file with the task class will be reloaded. If you modify another file and want to reload a task, restart the runner.
    """
    def __clear_removed_task_from_watch_data(self):
        for watch_metadata in self._watch_data.values():
            # set intersection
            watch_metadata.task_names &= set(self.runner.task_data.keys())

    def __add_new_tasks_to_watch_data(self):
        for task_metadata in self.runner.task_data.values():
            task_module = self._get_task_module(task_metadata)
            task_file = task_module.__file__

            if task_file not in self._watch_data:
                watch = self._fs_observer.schedule(self._fs_handler, task_file)
                self._watch_data[task_file] = WatchMetadata(watch, task_module, set())
                self.logger.info(f"Started monitoring file \"{task_file}\"")

            self._watch_data[task_file].task_names.add(task_metadata.name)

    def __clear_stale_watches_from_watch_data(self):
        for path, watch_metadata in self._watch_data.items():
            if len(watch_metadata.task_names) == 0:
                self._fs_observer.unschedule(watch_metadata.watch)
                self._watch_data.pop(path)
                self.logger.info(f"Stopped monitoring file \"{path}\"")

    @staticmethod
    def _get_task_module(task_metadata):
        return sys.modules[task_metadata.task_type.__module__]

    def _on_file_modified(self, event):
        watch_metadata = self._watch_data[event.src_path]
        watch_metadata.should_reload = True
        self.logger.info(f"File \"{event.src_path}\" was modified. Reloading on next execution.")

    def _update_watch_data(self):
        self.__clear_removed_task_from_watch_data()
        self.__add_new_tasks_to_watch_data()
        self.__clear_stale_watches_from_watch_data()

        self.logger.debug(f"Updated watch metadata. Current state:\n{self._watch_data}")

    def _reload_tasks(self, watch_metadata):
        self.logger.info(f"Reloading file \"{watch_metadata.watch.path}\". Tasks in file: {watch_metadata.task_names}")
        tasks_module = importlib.reload(watch_metadata.module)

        for name in watch_metadata.task_names:
            task_metadata = self.runner.task_data[name]
            self.runner.remove_task(name)
            task_metadata.task_type = getattr(tasks_module, task_metadata.task_type.__name__)
            self.runner.add_task(task_metadata)

    def setup(self):
        self._watch_data = {}
        self._fs_handler = FileSystemEventHandler()
        self._fs_handler.on_modified = self._on_file_modified
        self._fs_observer = Observer()
        self._fs_observer.start()

    def teardown(self):
        self._fs_observer.stop()
        self._fs_observer.join()
        self.logger.info("Stopped monitoring all files.")

    def execute(self):
        self._update_watch_data()
        for watch_metadata in self._watch_data.values():
            if watch_metadata.should_reload:
                self._reload_tasks(watch_metadata)
                watch_metadata.should_reload = False

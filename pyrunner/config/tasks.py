from pyrunner import tasks
from pyrunner.misc.types import TaskMetadata


TASKS = (
    TaskMetadata(name="task reloader", interval=5, task_type=tasks.TaskReloaderTask),
    TaskMetadata(name="ynet downloader", interval=10, task_type=tasks.URLDownloaderTask,
                 execute_kwargs={"url": "http://ynet.co.il", "output_path": "/usr/src/app/ynet.html"})
)

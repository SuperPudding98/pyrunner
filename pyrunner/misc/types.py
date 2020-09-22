from collections import namedtuple


TaskMetadata = namedtuple("TaskMetadata", (
    "name", "task", "interval", "class_name",
    "setup_args", "setup_kwargs",
    "teardown_args", "teardown_kwargs",
    "execute_args", "execute_kwargs"
))

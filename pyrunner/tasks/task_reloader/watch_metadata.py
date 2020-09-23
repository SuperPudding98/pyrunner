from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from watchdog.observers.api import ObservedWatch
    from typing import Set
    from types import ModuleType

from dataclasses import dataclass


@dataclass
class WatchMetadata:
    watch: ObservedWatch
    module: ModuleType
    task_names: Set[str]
    should_reload: bool = False

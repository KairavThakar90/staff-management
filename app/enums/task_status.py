from enum import Enum


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    completed = "completed"

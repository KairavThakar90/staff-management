from enum import Enum


class ProjectStatus(str, Enum):
    planning = "planning"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

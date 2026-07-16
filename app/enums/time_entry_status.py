from enum import Enum


class TimeEntryStatus(str, Enum):
    running = "running"
    stopped = "stopped"

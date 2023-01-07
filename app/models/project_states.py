from enum import Enum


class ProjectStates(str, Enum):
    CANCELLED = "CANCELLED"
    FINISHED = "FINISHED"
    PENDING = "PENDING"
    WIP = "WIP"

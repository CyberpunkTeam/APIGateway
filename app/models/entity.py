from enum import Enum


class Entity(str, Enum):
    USERS = "users"
    TEAMS = "teams"
    PROJECTS = "projects"

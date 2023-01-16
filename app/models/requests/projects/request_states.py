from enum import Enum


class RequestStates(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

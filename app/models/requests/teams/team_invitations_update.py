from enum import Enum
from json import loads
from typing import Optional
from pydantic import BaseModel


class States(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


class TeamInvitationUpdate(BaseModel):
    state: Optional[States] = ""

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

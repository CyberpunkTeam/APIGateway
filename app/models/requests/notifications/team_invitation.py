from json import loads
from typing import Optional

from pydantic import BaseModel


class TeamInvitation(BaseModel):
    sender_id: str
    receiver_id: str
    tid: str

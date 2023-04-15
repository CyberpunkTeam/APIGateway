from json import loads
from typing import Optional

from pydantic import BaseModel


class TeamMemberInternalRecommendations(BaseModel):
    sender_id: str
    receiver_id: str
    uid_recommendation: str
    tid: str

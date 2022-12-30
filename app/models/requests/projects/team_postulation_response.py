from json import loads
from typing import Optional

from pydantic import BaseModel

from app.models.requests.teams.team_invitations_update import States


class TeamPostulationResponse(BaseModel):
    ppid: str
    state: States

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

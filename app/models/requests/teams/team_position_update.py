from json import loads
from typing import Optional
from pydantic import BaseModel

from app.models.requests.teams.position_states import PositionStates
from app.models.requests.teams.requirements import Requirements


class TeamPositionUpdate(BaseModel):
    state: Optional[PositionStates]
    title: Optional[str]
    description: Optional[str]
    requirements: Optional[Requirements]

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

from json import loads
from typing import Optional

from pydantic.main import BaseModel

from app.models.requests.teams.requirements import Requirements


class TeamsPositions(BaseModel):
    title: str
    description: str
    tid: str
    requirements: Optional[Requirements]

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

from json import loads
from typing import List, Optional
from pydantic import BaseModel

from app.models.technologies import Technologies


class TeamUpdate(BaseModel):
    name: Optional[str] = ""
    technologies: Optional[Technologies]
    project_preferences: Optional[List[str]]
    idioms: Optional[List[str]]
    methodologies: Optional[List[str]]

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

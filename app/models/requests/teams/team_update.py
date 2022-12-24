from json import loads
from typing import List, Optional
from pydantic import BaseModel


class TeamUpdate(BaseModel):
    name: Optional[str] = ""
    technologies: Optional[List[str]]
    project_preferences: Optional[List[str]]
    created_date: Optional[str]
    updated_date: Optional[str]

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

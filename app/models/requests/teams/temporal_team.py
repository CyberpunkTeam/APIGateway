from json import loads
from pydantic.main import BaseModel


class TemporalTeams(BaseModel):
    name: str
    members: list
    skills: dict
    pid: str

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

from json import loads
from pydantic.main import BaseModel


class TeamsPositions(BaseModel):
    title: str
    description: str
    tid: str

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

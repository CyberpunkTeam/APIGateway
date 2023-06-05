from json import loads

from pydantic import BaseModel


class Tracks(BaseModel):
    uid: str
    path: str
    created_date: str

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

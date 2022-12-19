from typing import Optional
from json import loads
from pydantic import BaseModel


class UserUpdate(BaseModel):
    name: Optional[str] = ""
    lastname: Optional[str] = ""
    location: Optional[str] = ""

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

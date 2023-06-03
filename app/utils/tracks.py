from json import loads
from typing import Optional

from pydantic import BaseModel


class Tracks(BaseModel):
    uid: Optional[str] = None
    path: str
    created_date: str

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

    @staticmethod
    def get_schema():
        return {
            "uid": str,
            "path": str,
            "created_date": str,
        }

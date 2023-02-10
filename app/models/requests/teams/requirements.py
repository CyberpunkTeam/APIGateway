from json import loads
from typing import Optional, List

from pydantic.main import BaseModel


class Requirements(BaseModel):
    programming_language: Optional[List[str]] = []
    frameworks: Optional[List[str]] = []
    platforms: Optional[List[str]] = []
    cloud_providers: Optional[List[str]] = []
    databases: Optional[List[str]] = []

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

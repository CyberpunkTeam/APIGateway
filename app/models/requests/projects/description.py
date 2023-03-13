from json import loads
from typing import Optional, List

from pydantic import BaseModel


class Description(BaseModel):
    files_attached: Optional[dict] = {}
    functional_requirements: Optional[str] = ""
    non_function_requirements: Optional[List[str]] = []
    summary: Optional[str] = ""

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

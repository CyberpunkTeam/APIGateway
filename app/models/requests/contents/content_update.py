from json import loads
from typing import Optional

from pydantic import BaseModel


class ContentsUpdate(BaseModel):
    cid: Optional[str]
    title: Optional[str]
    tid: Optional[str]
    href: Optional[str]
    updated_date: Optional[str]
    cover_image: Optional[str]
    state: Optional[str]

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

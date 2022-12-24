from json import loads
from typing import Optional
from pydantic import BaseModel


class NotificationUpdate(BaseModel):
    viewed: Optional[bool] = False

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

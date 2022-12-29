from json import loads
from typing import Optional

from pydantic import BaseModel

from app.models.currency import Currency


class TeamPostulation(BaseModel):
    tid: str
    pid: str
    estimated_budget: int
    currency: Currency
    proposal_description: str

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

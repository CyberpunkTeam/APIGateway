from json import loads
from typing import Optional, List
from pydantic import BaseModel

from app.models.requests.projects.request_states import RequestStates


class ProjectAbandonment(BaseModel):
    pa_id: Optional[str]
    pid: str
    tid: str
    reasons: List[str]
    request_id: Optional[str]
    state: RequestStates

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

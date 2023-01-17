from typing import Optional

from pydantic import BaseModel

from app.models.requests.projects.request_states import RequestStates


class ProjectRequests(BaseModel):
    pid: str
    tid: str
    state: Optional[RequestStates]
    request_id: Optional[str] = None

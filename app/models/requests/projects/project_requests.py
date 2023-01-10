from pydantic import BaseModel


class ProjectRequests(BaseModel):
    pid: str
    tid: str

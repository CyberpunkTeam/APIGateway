from pydantic import BaseModel


class ProjectInvitation(BaseModel):
    tid: str
    pid: str

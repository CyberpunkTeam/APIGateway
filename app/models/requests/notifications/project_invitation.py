from json import loads
from typing import Optional

from pydantic import BaseModel


class ProjectInvitation(BaseModel):
    tid: str
    pid: str

from pydantic import BaseModel


class PositionInvitation(BaseModel):
    tpid: str
    uid: str

from pydantic import BaseModel


class TeamInvitation(BaseModel):
    sender_id: str
    receiver_id: str
    tid: str

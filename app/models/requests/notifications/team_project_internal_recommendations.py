from pydantic import BaseModel


class TeamProjectInternalRecommendations(BaseModel):
    sender_id: str
    receiver_id: str
    pid_recommendation: str
    tid: str

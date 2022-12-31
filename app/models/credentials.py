from pydantic import BaseModel


class Credentials(BaseModel):
    user_id: str
    auth_google_token: str

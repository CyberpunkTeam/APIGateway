from typing import Optional
from pydantic import BaseModel


class NotificationUpdate(BaseModel):
    viewed: Optional[bool] = False

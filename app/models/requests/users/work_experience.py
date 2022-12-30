from typing import Optional

from pydantic import BaseModel


class WorkExperience(BaseModel):
    position: str
    company: str
    start_date: str
    finish_date: Optional[str]
    current_job: bool

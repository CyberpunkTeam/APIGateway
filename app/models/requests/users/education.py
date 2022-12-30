from typing import Optional

from pydantic import BaseModel


class Education(BaseModel):
    title: str
    institution: str
    start_date: str
    finish_date: Optional[str]
    finished: bool

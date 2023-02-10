from typing import Optional, List
from json import loads
from pydantic import BaseModel

from app.models.requests.users.education import Education
from app.models.requests.users.skills import Skills
from app.models.requests.users.work_experience import WorkExperience


class UserUpdate(BaseModel):
    name: Optional[str] = ""
    lastname: Optional[str] = ""
    location: Optional[str] = ""
    profile_image: Optional[str] = ""
    cover_image: Optional[str] = ""
    education: Optional[List[Education]] = []
    work_experience: Optional[List[WorkExperience]] = []
    skills: Optional[Skills]
    idioms: Optional[List[str]]

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

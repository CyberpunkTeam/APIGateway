import uuid
from json import loads
from typing import Optional, List

from pydantic import BaseModel

from app.models.currency import Currency
from app.models.project_states import ProjectStates
from app.models.technologies import Technologies
from app.models.unit_duration import UnitDuration


class ProjectsUpdate(BaseModel):
    name: Optional[str] = None
    idioms: Optional[List[str]] = None
    description: Optional[str] = None
    technologies: Optional[Technologies]
    updated_date: Optional[str] = ""
    state: Optional[ProjectStates] = None
    team_assigned: Optional[str] = None
    tentative_budget: Optional[float]
    budget_currency: Optional[Currency]
    tentative_duration: Optional[int]
    unit_duration: Optional[UnitDuration]

    def to_json(self):
        return loads(self.json(exclude_defaults=True))

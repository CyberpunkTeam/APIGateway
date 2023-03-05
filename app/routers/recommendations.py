from fastapi import APIRouter

from app import config
from app.services import Services

router = APIRouter()


@router.post("/recommendations/projects/", tags=["recommendations"], status_code=201)
async def create_team_recommendations(project: dict):
    url = config.RECOMMENDATION_SERVICE_URL
    resource = "recommendations/projects/"
    params = {}
    return Services.post(url, resource, params, project)

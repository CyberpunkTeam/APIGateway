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


@router.post(
    "/recommendations/models/{recommender_name}",
    tags=["recommendations"],
    status_code=201,
)
async def create_team_recommendations(recommender_name: str):
    url = config.RECOMMENDATION_SERVICE_URL
    resource = f"/recommendations/models/{recommender_name}/training"
    params = {}
    return Services.post(url, resource, params, {})

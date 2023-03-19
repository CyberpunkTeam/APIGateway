from fastapi import APIRouter

from app import config
from app.routers.teams import _get_team
from app.services import Services

router = APIRouter()


@router.post("/recommendations/projects/", tags=["recommendations"], status_code=201)
async def create_team_recommendations(project: dict):
    return _get_team_recommendations(project)


def _get_team_recommendations(project):
    url = config.RECOMMENDATION_SERVICE_URL
    resource = "recommendations/projects/"
    params = {}
    tids = Services.post(url, resource, params, project)

    teams = [_get_team(tid) for tid in tids]
    teams = list(
        filter(
            lambda team: team.get("owner") != project.get("creator", {}).get("uid"),
            teams,
        )
    )

    teams = list(
        sorted(teams, key=lambda team: team.get("overall_rating"), reverse=True)
    )
    return teams


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

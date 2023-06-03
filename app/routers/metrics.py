from fastapi import APIRouter

from app import config
from app.services import Services

router = APIRouter()


@router.get("/metrics", tags=["metrics"])
async def get_metrics():
    url_projects = config.PROJECT_SERVICE_URL
    url_teams = config.TEAM_SERVICE_URL
    url_users = config.USER_SERVICE_URL
    resource = "metrics"
    params = {}

    projects_req = Services.get(url_projects, resource, params, async_mode=True)
    teams_req = Services.get(url_teams, resource, params, async_mode=True)
    users_req = Services.get(url_users, resource, params, async_mode=True)

    projects, teams, users = Services.execute_many([projects_req, teams_req, users_req])

    result = {"projects": projects, "teams": teams, "users": users}

    return result

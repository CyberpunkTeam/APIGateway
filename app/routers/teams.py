from fastapi import APIRouter
from app import config
from app.services import Services

router = APIRouter()


@router.post("/teams/", tags=["teams"], status_code=201)
async def create_team(body: dict):
    url = config.TEAM_SERVICE_URL
    resource = "teams/"
    params = {}
    return Services.post(url, resource, params, body)

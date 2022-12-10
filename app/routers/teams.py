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


@router.get("/teams/:tid", tags=["teams"], status_code=200)
async def get_team(tid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    return Services.get(url, resource, params)


@router.post("/teams/{tid}/members/{mid}", tags=["teams"], status_code=201)
async def add_member(tid: str, mid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}/members/{mid}"
    params = {}
    return Services.post(url, resource, params)

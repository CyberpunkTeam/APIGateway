from fastapi import APIRouter
from app import config
from app.models.requests.teams.team_update import TeamUpdate
from app.services import Services

router = APIRouter()


@router.post("/teams/", tags=["teams"], status_code=201)
async def create_team(body: dict):
    url = config.TEAM_SERVICE_URL
    resource = "teams/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/teams/{tid}", tags=["teams"], status_code=200)
async def get_team(tid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    team = Services.get(url, resource, params)

    members = team["members"]
    query_param = "[" + ",".join(members) + "]"

    url = config.USER_SERVICE_URL
    resource = f"users/?uids={query_param}"
    members_info = Services.get(url, resource, params)

    team["members"] = members_info
    return team


@router.post("/teams/{tid}/members/{mid}", tags=["teams"], status_code=201)
async def add_member(tid: str, mid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}/members/{mid}"
    params = {}
    return Services.post(url, resource, params)


@router.put("/teams/{tid}", tags=["teams"])
async def put_user(tid: str, team_update: TeamUpdate):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    return Services.put(url, resource, params, team_update.to_json())

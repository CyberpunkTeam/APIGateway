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


@router.get("/teams/", tags=["teams"], status_code=200)
async def get_teams(owner: str = None):
    url = config.TEAM_SERVICE_URL
    resource = "teams/"
    params = {}
    if owner is not None:
        params["owner"] = owner

    teams = Services.get(url, resource, params)

    if owner is not None:
        req_members = []
        for team in teams:
            members = team["members"]
            query_param = "[" + ",".join(members) + "]"
            print(f"query_param: {query_param}")
            url = config.USER_SERVICE_URL
            resource = "users/"
            params = {"uids": query_param}
            req_members_info = Services.get(url, resource, params, async_mode=True)
            req_members.append(req_members_info)

        members_info = Services.execute_many(req_members)
        for i in range(len(teams)):
            teams[i]["members"] = members_info[i]

    return teams


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

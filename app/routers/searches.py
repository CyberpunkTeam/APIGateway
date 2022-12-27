from fastapi import APIRouter, HTTPException

from app import config
from app.models.entity import Entity
from app.services import Services

router = APIRouter()


@router.get("/searches/", tags=["searches"])
async def search(word: str):
    result = {}
    params = {"search": word}

    url = config.USER_SERVICE_URL
    resource = f"users/"
    req_users = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/"
    req_teams = Services.get(url, resource, params, async_mode=True)

    users, teams = Services.execute_many([req_users, req_teams])

    result["teams"] = teams
    result["users"] = users
    return result


@router.get("/searches/{entity}", tags=["searches"])
async def search(entity: Entity = None, word: str = ""):
    if word == "":
        raise HTTPException(status_code=400, detail="Word must not be empty")

    result = {}
    params = {"search": word}
    if entity == Entity.USERS:
        url = config.USER_SERVICE_URL
        resource = f"users/"
        users = Services.get(url, resource, params)
        result["users"] = users
    elif entity == Entity.TEAMS:
        url = config.TEAM_SERVICE_URL
        resource = f"teams/"
        teams = Services.get(url, resource, params)
        result["teams"] = teams
    return result

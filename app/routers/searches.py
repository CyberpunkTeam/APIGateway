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

    url = config.CONTENT_SERVICE_URL
    resource = f"contents/"
    req_contents = Services.get(url, resource, params, async_mode=True)

    url = config.USER_SERVICE_URL
    resource = f"users/"
    req_users_blocked = Services.get(
        url, resource, {"state": "BLOCKED"}, async_mode=True
    )

    url = config.TEAM_SERVICE_URL
    resource = f"teams/"
    req_teams_blocked = Services.get(
        url, resource, {"state": "BLOCKED"}, async_mode=True
    )

    url = config.CONTENT_SERVICE_URL
    resource = f"contents/"
    req_contents_blocked = Services.get(
        url, resource, {"state": "BLOCKED"}, async_mode=True
    )

    (
        users,
        teams,
        contents,
        users_blocked,
        teams_blocked,
        contents_blocked,
    ) = Services.execute_many(
        [
            req_users,
            req_teams,
            req_contents,
            req_users_blocked,
            req_teams_blocked,
            req_contents_blocked,
        ]
    )
    teams_blocked = [team.get("tid") for team in teams_blocked]
    users_blocked = [user.get("uid") for user in users_blocked]
    contents_blocked = [content.get("cid") for content in contents_blocked]

    result["teams"] = [team for team in teams if not (team.get("tid") in teams_blocked)]
    result["users"] = [user for user in users if not (user.get("uid") in users_blocked)]
    result["contents"] = [
        content for content in contents if not (content.get("cid") in contents_blocked)
    ]
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


@router.get("/locations/", tags=["searches"])
async def search_location(word: str = ""):
    params = {"search": word}
    url = config.USER_SERVICE_URL
    resource = "locations/"
    return Services.get(url, resource, params)

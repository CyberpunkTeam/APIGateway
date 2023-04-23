from fastapi import APIRouter
from app.services import Services
from app import config

router = APIRouter()


@router.post("/contents/", tags=["contents"], status_code=201)
async def create_content(body: dict):
    url = config.CONTENT_SERVICE_URL
    resource = "contents/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/contents/", tags=["contents"], status_code=200)
async def get_contents(author_uid: str = None, tid: str = None):
    url = config.CONTENT_SERVICE_URL
    resource = "contents/"
    params = {}
    if author_uid is not None:
        params["author_uid"] = author_uid
    if tid is not None:
        params["tid"] = tid

    return Services.get(url, resource, params)


@router.get("/contents/{cid}", tags=["contents"], status_code=200)
async def get_contents(cid: str = None):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}"
    params = {}

    contents = Services.get(url, resource, params)

    reqs = []

    for content in contents:
        uid = content.get("author_uid")
        url = config.USER_SERVICE_URL
        resource = f"users/{uid}"
        params = {}
        req = Services.get(url, resource, params, async_mode=True)
        reqs.append(req)
    users = Services.execute_many(reqs)

    for i in range(len(contents)):
        content = contents[i]
        user = users[i]
        content["author"] = user

    team_contents = [content for content in contents if content.get("tid") is not None]
    users_contents = [content for content in contents if content.get("tid") is None]

    reqs_team = []
    for j in range(len(team_contents)):
        team = team_contents[j]
        url = config.TEAM_SERVICE_URL
        resource = f"teams/{team.get('tid')}"
        params = {}
        req = Services.get(url, resource, params, async_mode=True)
        reqs_team.append(req)

    teams = Services.execute_many(reqs_team)

    for j in range(len(team_contents)):
        content = team_contents[j]
        team = teams[j]
        content["team"] = team

    return team_contents + users_contents

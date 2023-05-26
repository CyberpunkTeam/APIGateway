from fastapi import APIRouter

from app.models.requests.contents.content_update import ContentsUpdate
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
async def get_contents(author_uid: str = None, tid: str = None, state: str = None):
    url = config.CONTENT_SERVICE_URL
    resource = "contents/"
    params = {}
    if author_uid is not None:
        params["author_uid"] = author_uid
    if tid is not None:
        params["tid"] = tid
    if state is not None:
        params["state"] = state

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


@router.get("/contents/{cid}", tags=["contents"], status_code=200)
async def get_contents(cid: str = None):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}"
    params = {}

    content = Services.get(url, resource, params)
    return _complete_content(content)


@router.delete("/contents/{cid}", tags=["contents"])
async def delete_content(cid: str):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}"
    params = {}
    return Services.delete(url, resource, params)


@router.put("/contents/{cid}", tags=["contents"])
async def put_content(cid: str, content_update: ContentsUpdate):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}"
    params = {}
    content = Services.put(url, resource, params, content_update.to_json())
    return _complete_content(content)


def _complete_content(content):
    uid = content.get("author_uid")
    url = config.USER_SERVICE_URL
    resource = f"users/{uid}"
    params = {}
    user = Services.get(url, resource, params)

    content["author"] = user

    if content.get("tid") is not None:
        url = config.TEAM_SERVICE_URL
        resource = f"teams/{content.get('tid')}"
        params = {}
        team = Services.get(url, resource, params)
        content["team"] = team

    return content


@router.delete("/contents/{cid}/likes/{uid}", tags=["contents"])
async def delete_like_to_content(cid: str, uid: str):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}/likes/{uid}"
    params = {}
    return Services.delete(url, resource, params)


@router.post("/contents/{cid}/likes/{uid}", tags=["contents"])
async def add_like_to_content(cid: str, uid: str):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}/likes/{uid}"
    params = {}
    return Services.post(url, resource, params)


@router.post("/contents/{cid}/blocked", tags=["contents"])
async def block_content(cid: str):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}"
    params = {}
    content_update = ContentsUpdate(state="BLOCKED")
    return Services.put(url, resource, params, content_update.to_json())


@router.post("/contents/{cid}/unblocked", tags=["contents"])
async def block_uncontent(cid: str):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}"
    params = {}
    content_update = ContentsUpdate(state="ACTIVE")
    return Services.put(url, resource, params, content_update.to_json())

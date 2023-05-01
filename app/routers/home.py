from fastapi import APIRouter, Header, HTTPException
from app import config
from app.services import Services

router = APIRouter()


@router.get("/home/{uid}", tags=["home"])
async def get_home(uid: str):
    url = config.USER_SERVICE_URL
    resource = f"users/{uid}"
    params = {}
    user = Services.get(url, resource, params)

    following = user["following"]
    uids = following["users"]
    tids = following["teams"]

    contents = []
    reqs_content = []
    for uid_following in uids:
        url = config.CONTENT_SERVICE_URL
        resource = "contents/"
        params = {}
        params["author_uid"] = uid_following
        reqs = Services.get(url, resource, params, async_mode=True)
        reqs_content.append(reqs)

    if len(reqs_content) > 0:
        contents = Services.execute_many(reqs_content)

    contents = filter(lambda ele: len(ele) > 0, contents)

    return contents

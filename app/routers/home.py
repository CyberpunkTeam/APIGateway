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

    reqs = []
    for uid in uids:
        url = config.USER_SERVICE_URL
        resource = f"users/{uid}"
        params = {}
        req = Services.get(url, resource, params, async_mode=True)
        reqs.append(req)
    users = Services.execute_many(reqs)

    users_dict = {user.get("uid"): user for user in users}

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

    contents = list(filter(lambda ele: len(ele) > 0, contents))

    content_result = []
    for content in contents:
        content_result += content

    results = [
        _create_home_content("content", content, users_dict)
        for content in content_result
    ]

    return results


def _create_home_content(content_type, content, users_dict):
    creator = _get_content_creator(content_type, content, users_dict)

    return {"content": content, "content_type": content_type, "creator": creator}


def _get_content_creator(content_type, content, users_dict):
    if content_type == "content":
        uid = content.get("author_uid")

        return users_dict.get(uid)

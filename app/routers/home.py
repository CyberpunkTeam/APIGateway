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
    users_dict = _get_users(uids)

    tids = following["teams"]
    teams_dict = _get_teams(tids)

    users_contents = _get_content(uids=uids, dict_source=users_dict)

    teams_contents = _get_content(tids=tids, dict_source=teams_dict)

    results = users_contents + teams_contents

    _order_contents_home(results)

    return results


def _order_contents_home(contents):
    return contents.sort(key=lambda x: x["created_date"], reverse=True)


def _create_home_content(content_type, content, users_dict):
    creator = _get_content_creator(content_type, content, users_dict)
    created_date = _get_content_created_date(content_type, content)
    return {
        "content": content,
        "content_type": content_type,
        "creator": creator,
        "created_date": created_date,
    }


def _get_content_created_date(content_type, content):
    if content_type == "content_by_user":
        return content.get("created_date")

    if content_type == "content_by_team":
        return content.get("created_date")


def _get_content_creator(content_type, content, dict_source):
    if content_type == "content_by_user":
        uid = content.get("author_uid")

        return dict_source.get(uid)

    if content_type == "content_by_team":
        tid = content.get("tid")

        return dict_source.get(tid)


def _get_users(uids):
    reqs = []
    for uid in uids:
        url = config.USER_SERVICE_URL
        resource = f"users/{uid}"
        params = {}
        req = Services.get(url, resource, params, async_mode=True)
        reqs.append(req)
    users = Services.execute_many(reqs)

    return {user.get("uid"): user for user in users}


def _get_teams(tids):
    reqs = []
    for tid in tids:
        url = config.TEAM_SERVICE_URL
        resource = f"teams/{tid}"
        params = {}
        req = Services.get(url, resource, params, async_mode=True)
        reqs.append(req)
    teams = Services.execute_many(reqs)

    return {team.get("tid"): team for team in teams}


def _get_content(uids=None, tids=None, dict_source=None):
    param = "author_uid" if uids is not None else "tid"
    content_type = "content_by_user" if uids is not None else "content_by_team"
    elements = uids if uids is not None else tids
    contents = []
    reqs_content = []
    for value in elements:
        url = config.CONTENT_SERVICE_URL
        resource = "contents/"
        params = {param: value}
        reqs = Services.get(url, resource, params, async_mode=True)
        reqs_content.append(reqs)

    if len(reqs_content) > 0:
        contents = Services.execute_many(reqs_content)

    contents = list(filter(lambda ele: len(ele) > 0, contents))
    content_result = []
    for content in contents:
        content_result += content

    results_contents_by_users = [
        _create_home_content(content_type, content, dict_source)
        for content in content_result
    ]
    return results_contents_by_users

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
    uids = [uids for uid in uids if uid in users_dict]

    tids = following["teams"]
    teams_dict = _get_teams(tids)
    tids = [tid for tid in tids if tid in teams_dict]

    users_contents = _get_content(uids=uids, dict_source=users_dict)

    teams_contents = _get_content(tids=tids, dict_source=teams_dict)

    new_projects = _get_new_projects(uids, users_dict)

    new_teams = _get_new_teams(uids, users_dict)

    results = users_contents + teams_contents + new_projects + new_teams

    _order_contents_home(results)

    return results


def _order_contents_home(contents):
    return contents.sort(
        key=lambda x: _get_date_to_compare(x["created_date"]), reverse=True
    )


def _get_date_to_compare(date):
    datetime_list = date.split(":")
    times = ":".join(datetime_list[1:])
    date_list = datetime_list[0].split("-")
    day = date_list[0]
    month = date_list[1]
    year = date_list[2]
    return f"{year}-{month}-{day}:{times}"


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

    if content_type == "new_project":
        return content.get("created_date")

    if content_type == "new_team":
        return content.get("created_date")


def _get_content_creator(content_type, content, dict_source):
    if content_type == "content_by_user":
        uid = content.get("author_uid")

        return dict_source.get(uid)

    if content_type == "content_by_team":
        tid = content.get("tid")

        return dict_source.get(tid)

    if content_type == "new_project":
        uid = content.get("creator_uid")

        return dict_source.get(uid)

    if content_type == "new_team":
        uid = content.get("owner")

        return dict_source.get(uid)


def _get_users(uids):
    if len(uids) > 0:
        uids = "[" + ",".join(uids) + "]"
        url = config.USER_SERVICE_URL
        params = {"uids": uids}
        resource = "users/"
        users = Services.get(url, resource, params)
    else:
        users = []

    return {user.get("uid"): user for user in users if user.get("state") == "ACTIVE"}


def _get_teams(tids):
    if len(tids) > 0:
        url = config.TEAM_SERVICE_URL
        tids = "[" + ",".join(tids) + "]"
        params = {"tids": tids}
        resource = f"teams/"
        teams = Services.get(url, resource, params)
    else:
        teams = []

    return {team.get("tid"): team for team in teams if team.get("state") == "ACTIVE"}


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
        if content.get("state") == "ACTIVE"
    ]
    return results_contents_by_users


def _get_new_projects(uids, user_dict):
    projects = []
    reqs_project = []
    for uid in uids:
        url = config.PROJECT_SERVICE_URL
        resource = "projects/"
        params = {"creator_uid": uid}
        reqs = Services.get(url, resource, params, async_mode=True)
        reqs_project.append(reqs)

    if len(reqs_project) > 0:
        projects = Services.execute_many(reqs_project)

    projects = list(filter(lambda ele: len(ele) > 0, projects))
    projects_result = []
    for project in projects:
        projects_result += project

    projects_result = [
        _create_home_content("new_project", project, user_dict)
        for project in projects_result
        if project.get("internal_state") == "ACTIVE"
    ]
    return projects_result


def _get_new_teams(uids, user_dict):
    teams = []
    reqs_team = []
    for uid in uids:
        url = config.TEAM_SERVICE_URL
        resource = "teams/"
        params = {"owner": uid}
        reqs = Services.get(url, resource, params, async_mode=True)
        reqs_team.append(reqs)

    if len(reqs_team) > 0:
        teams = Services.execute_many(reqs_team)

    teams = list(filter(lambda ele: len(ele) > 0, teams))
    teams_result = []
    for team in teams:
        teams_result += team

    teams_result = [
        _create_home_content("new_team", team, user_dict)
        for team in teams_result
        if team.get("state") == "ACTIVE"
    ]
    return teams_result

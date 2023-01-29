from fastapi import APIRouter
from app import config
from app.models.project_states import ProjectStates
from app.models.requests.projects.project_update import ProjectsUpdate
from app.models.requests.teams.position_states import PositionStates
from app.models.requests.teams.team_position_update import TeamPositionUpdate
from app.models.requests.teams.team_update import TeamUpdate
from app.models.requests.teams.teams_positions import TeamsPositions
from app.routers.notifications import (
    send_new_candidate_notification,
    send_position_postulation_accepted_notification,
)
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
    members_info_req = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = "teams_reviews/"
    params = {"tid": tid}

    reviews_req = Services.get(url, resource, params, async_mode=True)

    reviews, members_info = Services.execute_many([reviews_req, members_info_req])

    total_ratings = 0
    amount_ratings = 0
    for review in reviews:
        amount_ratings += 1
        total_ratings += review.get("rating", 0)

    team["overall_rating"] = round(
        float(total_ratings) / amount_ratings if amount_ratings > 0 else 0, 1
    )
    team["reviews"] = reviews
    team["members"] = members_info
    return team


@router.post("/teams/{tid}/members/{mid}", tags=["teams"], status_code=201)
async def add_member(tid: str, mid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}/members/{mid}"
    params = {}
    new_members = Services.post(url, resource, params)

    url = config.USER_SERVICE_URL
    resource = f"users/{mid}"
    params = {}
    req_user = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    user, team = Services.execute_many([req_user, req_team])

    notification = {
        "sender_id": mid,
        "receiver_id": team.get("owner"),
        "notification_type": "NEW_TEAM_MEMBERS",
        "resource": "USERS",
        "resource_id": mid,
        "metadata": {"user": user, "team": team},
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    Services.post(url, resource, params, notification)

    return new_members


@router.put("/teams/{tid}", tags=["teams"])
async def put_user(tid: str, team_update: TeamUpdate):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    return Services.put(url, resource, params, team_update.to_json())


@router.post("/teams_reviews/", tags=["teams"], status_code=201)
async def create_team_review(body: dict):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{body.get('pid')}"
    project_update = ProjectsUpdate(state=ProjectStates.FINISHED)
    params = {}
    Services.put(url, resource, params, project_update.to_json())

    url = config.TEAM_SERVICE_URL
    resource = "teams_reviews/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/teams_reviews/", tags=["teams"], status_code=200)
async def get_team_review(pid: str = None, tid: str = None):
    url = config.TEAM_SERVICE_URL
    resource = "teams_reviews/"
    params = {}
    if pid is not None:
        params["pid"] = pid
    if tid is not None:
        params["tid"] = tid

    reviews = Services.get(url, resource, params)

    if tid is not None:
        reqs = []
        for review in reviews:
            pid = review.get("pid")
            url = config.PROJECT_SERVICE_URL
            resource = f"projects/{pid}"
            params = {}
            req_project = Services.get(url, resource, params, async_mode=True)
            reqs.append(req_project)

        projects = Services.execute_many(reqs)

        for i in range(len(reviews)):
            reviews[i]["project"] = projects[i]

    return reviews


@router.post("/team_members_reviews/", tags=["teams"], status_code=201)
async def create_team_member_review(body: dict):
    url = config.TEAM_SERVICE_URL
    resource = "team_members_reviews/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/team_members_reviews/", tags=["teams"], status_code=200)
async def get_team_member_review(
    pid: str = None,
    tid: str = None,
    member_reviewer: str = None,
    member_reviewed: str = None,
):
    url = config.TEAM_SERVICE_URL
    resource = "team_members_reviews/"
    params = {}
    if pid is not None:
        params["pid"] = pid
    if tid is not None:
        params["tid"] = tid
    if member_reviewer is not None:
        params["member_reviewer"] = member_reviewer
    if member_reviewed is not None:
        params["member_reviewed"] = member_reviewed
    return Services.get(url, resource, params)


@router.post("/teams_positions/", tags=["teams"], status_code=201)
async def create_team_position(team_position: TeamsPositions):
    url = config.TEAM_SERVICE_URL
    resource = "teams_positions/"
    params = {}
    return Services.post(url, resource, params, team_position.to_json())


@router.get("/teams_positions/", tags=["teams"], status_code=200)
async def list_team_position(tid: str = None, state: PositionStates = None):
    url = config.TEAM_SERVICE_URL
    resource = "teams_positions/"
    params = {}
    if tid is not None:
        params["tid"] = tid
    if state is not None:
        params["state"] = state

    positions = Services.get(url, resource, params)
    candidates_reqs = []
    if tid is not None:
        for position in positions:
            canditates = position["canditates"]
            query_param = "[" + ",".join(canditates) + "]"
            url = config.USER_SERVICE_URL
            resource = "users/"
            params = {"uids": query_param}
            candidates_req = Services.get(url, resource, params, async_mode=True)
            candidates_reqs.append(candidates_req)

        candidates_info = Services.execute_many(candidates_reqs)
        for i in range(len(positions)):
            positions[i]["canditates"] = candidates_info[i]
    return positions


@router.get("/teams_positions/{tpid}", tags=["teams"], status_code=200)
async def get_team_position(tpid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"teams_positions/{tpid}"
    params = {}

    return Services.get(url, resource, params)


@router.put("/teams_positions/{tpid}", tags=["teams"], status_code=200)
async def update_team_position(tpid: str, body: TeamPositionUpdate):
    url = config.TEAM_SERVICE_URL
    resource = f"teams_positions/{tpid}"
    params = {}

    return Services.put(url, resource, params, body.to_json())


@router.post(
    "/teams_positions/{tpid}/candidates/{uid}",
    tags=["teams"],
)
async def add_candidate(tpid: str, uid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"/teams_positions/{tpid}/candidates/{uid}"
    params = {}
    result = Services.post(url, resource, params)

    send_new_candidate_notification(tpid, uid)

    return result


@router.delete(
    "/teams_positions/{tpid}/candidates/{uid}",
    tags=["teams"],
)
async def remove_candidate(tpid: str, uid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"/teams_positions/{tpid}/candidates/{uid}"
    params = {}

    return Services.delete(url, resource, params)


@router.post("/teams/{tid}/teams_positions/{tpid}/candidates/{uid}", tags=["teams"])
async def accept_candidate(tid: str, tpid: str, uid: str):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}/members/{uid}"
    params = {}

    new_members = Services.post(url, resource, params)

    url = config.TEAM_SERVICE_URL
    resource = f"/teams_positions/{tpid}/candidates/{uid}"
    params = {}

    Services.delete(url, resource, params)

    send_position_postulation_accepted_notification(tpid, uid)

    return new_members

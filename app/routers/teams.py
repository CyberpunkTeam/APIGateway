from fastapi import APIRouter
from app import config
from app.models.project_states import ProjectStates
from app.models.requests.projects.project_update import ProjectsUpdate
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

    url = config.PROJECT_SERVICE_URL
    resource = "projects_reviews/"
    params = {"tid": tid}

    reviews_req = Services.get(url, resource, params, async_mode=True)

    reviews, members_info = Services.execute_many([reviews_req, members_info_req])

    total_ratings = 0
    amount_ratins = 0
    for review in reviews:
        amount_ratins += 1
        total_ratings += review.get("rating", 0)

    team["overall_rating"] = (
        float(total_ratings) / amount_ratins if amount_ratins > 0 else 0
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
    return Services.get(url, resource, params)


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

from typing import Union

from fastapi import APIRouter, Header, HTTPException
from app import config
from app.models.project_states import ProjectStates
from app.models.requests.projects.project_update import ProjectsUpdate
from app.models.requests.teams.position_states import PositionStates
from app.models.requests.teams.team_position_update import TeamPositionUpdate
from app.models.requests.teams.team_update import TeamUpdate
from app.models.requests.teams.teams_positions import TeamsPositions
from app.models.requests.teams.temporal_team import TemporalTeams
from app.routers.notifications import (
    send_new_candidate_notification,
    send_position_postulation_accepted_notification,
    send_team_review_notification,
    send_new_temporal_team_notification,
    send_invitation_to_projects,
)
from app.services import Services
from app.utils.authenticator import Authenticator

router = APIRouter()


@router.post("/teams/", tags=["teams"], status_code=201)
async def create_team(body: dict):
    url = config.TEAM_SERVICE_URL
    resource = "teams/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/teams/", tags=["teams"], status_code=200)
async def get_teams(owner: str = None, mid: str = None, tids: str = None):
    url = config.TEAM_SERVICE_URL
    resource = "teams/"
    params = {}
    if owner is not None:
        params["owner"] = owner

    if mid is not None:
        params["mid"] = mid

    if tids is not None:
        params["tids"] = tids

    teams = Services.get(url, resource, params)

    if owner is not None or mid is not None:
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
    return _get_team(tid)


def _get_team(tid: str):
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
async def put_team(
    tid: str,
    team_update: TeamUpdate,
    x_tiger_token: Union[str, None] = Header(default=None),
):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    team = Services.get(url, resource, params)
    team_owner = team.get("owner")
    token_user = Authenticator.get_user_id(x_tiger_token.replace("Bearer ", ""))

    if team_owner != token_user:
        raise HTTPException(
            status_code=401,
            detail="Only team owner can update his team",
        )

    return Services.put(url, resource, params, team_update.to_json())


@router.post("/teams_reviews/", tags=["teams"], status_code=201)
async def create_team_review(body: dict):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{body.get('pid')}"
    project_update = ProjectsUpdate(state=ProjectStates.FINISHED)
    params = {}
    project = Services.put(url, resource, params, project_update.to_json())

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{body.get('tid')}"
    params = {}
    team = Services.get(url, resource, params)

    send_team_review_notification(team, project)

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
async def list_team_position(
    tid: str = None,
    state: PositionStates = None,
    programming_languages: str = None,
    frameworks: str = None,
    platforms: str = None,
    databases: str = None,
):
    url = config.TEAM_SERVICE_URL
    resource = "teams_positions/"
    params = {}
    if tid is not None:
        params["tid"] = tid
    if state is not None:
        params["state"] = state
    if programming_languages is not None:
        params["programming_languages"] = programming_languages
    if frameworks is not None:
        params["frameworks"] = frameworks
    if platforms is not None:
        params["platforms"] = platforms
    if databases is not None:
        params["databases"] = databases

    positions = Services.get(url, resource, params)

    candidates_reqs = []
    if tid is not None:
        for position in positions:
            candidates = position["candidates"]
            query_param = "[" + ",".join(candidates) + "]"
            url = config.USER_SERVICE_URL
            resource = "users/"
            params = {"uids": query_param}
            candidates_req = Services.get(url, resource, params, async_mode=True)
            candidates_reqs.append(candidates_req)

        candidates_info = Services.execute_many(candidates_reqs)
        for i in range(len(positions)):
            positions[i]["candidates"] = candidates_info[i]

    if state == PositionStates.OPEN and tid is not None:
        uids = []
        for position in positions:
            url = config.RECOMMENDATION_SERVICE_URL
            resource = "recommendations/teams_positions/"
            params = {}
            position_i = dict(position)
            del position_i["candidates"]
            uids_i = Services.post(url, resource, params, position_i)
            uids.append(uids_i)
        # uids = Services.execute_many(reqs)
        for i in range(len(positions)):
            position_i = positions[i]
            uids_i = uids[i]
            reqs_user = []
            for uid in uids_i:
                url = config.USER_SERVICE_URL
                resource = f"users/{uid}"
                reqs_user.append(Services.get(url, resource, params, async_mode=True))
            if len(reqs_user) > 0:
                users = Services.execute_many(reqs_user)
                for user in users:
                    url = config.NOTIFICATION_SERVICE_URL
                    resource = "notifications/"
                    params = {
                        "receiver_id": user.get("uid"),
                        "sender_id": tid,
                        "resource_id": position_i.get("tpid"),
                    }
                    resp = Services.get(url, resource, params)
                    user["invitation_sent"] = len(resp) > 0
                position_i["users_recommendation"] = users
            else:
                position_i["users_recommendation"] = []

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


@router.post("/teams/temporal", tags=["teams"])
async def create_temporal_team(temporal_team: TemporalTeams):
    body = {
        "name": temporal_team.name,
        "project_preferences": [],
        "members": [member.get("uid") for member in temporal_team.members],
        "technologies": temporal_team.skills,
        "temporal": True,
    }

    resource = "teams/"
    params = {}
    url = config.TEAM_SERVICE_URL

    team = Services.post(url, resource, params, body)

    resource = "temporal_teams_registers/"
    params = {}
    url = config.TEAM_SERVICE_URL
    body_register = {"pid": temporal_team.pid, "tid": team.get("tid")}
    Services.post(url, resource, params, body_register)

    send_new_temporal_team_notification(body.get("members"), team)
    send_invitation_to_projects(body.get("members"), temporal_team.pid, team)

    return _get_team(team.get("tid"))


@router.get("/teams/temporal/", tags=["teams"], status_code=200)
async def create_team_recommendations(pid: str):
    resource = f"temporal_teams_registers/?pid={pid}"
    params = {}
    url = config.TEAM_SERVICE_URL
    result = Services.get(url, resource, params)
    if len(result) > 0:
        return list(map(lambda result_i: _get_team(result_i.get("tid")), result))

    return result

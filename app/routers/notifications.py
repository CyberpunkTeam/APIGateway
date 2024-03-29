from typing import Union

from fastapi import APIRouter, Header, HTTPException
from app import config

from app.models.requests.notifications.notification_update import NotificationUpdate
from app.models.requests.notifications.position_invitation import PositionInvitation
from app.models.requests.notifications.project_invitation import ProjectInvitation
from app.models.requests.notifications.team_invitation import TeamInvitation
from app.models.requests.notifications.team_member_internal_recommendations import (
    TeamMemberInternalRecommendations,
)
from app.models.requests.notifications.team_project_internal_recommendations import (
    TeamProjectInternalRecommendations,
)
from app.models.requests.projects.project_abandonment import ProjectAbandonment
from app.models.requests.projects.project_abandons_request import (
    ProjectAbandonsRequests,
)
from app.models.requests.projects.project_requests import ProjectRequests

from app.models.requests.projects.request_states import RequestStates
from app.models.requests.projects.team_postulation import TeamPostulation
from app.models.requests.projects.team_postulation_response import (
    TeamPostulationResponse,
)
from app.services import Services
from app.utils.authenticator import Authenticator

router = APIRouter()


@router.post("/notifications/team_invitation/", tags=["notifications"], status_code=201)
async def create_notification(body: TeamInvitation):
    url = config.TEAM_SERVICE_URL
    resource = f"/team_invitations/"
    body_invitation = {
        "tid": body.tid,
        "team_owner_uid": body.sender_id,
        "postulant_uid": body.receiver_id,
    }
    params = {}
    team_invitation = Services.post(url, resource, params, body_invitation)

    url = config.USER_SERVICE_URL
    resource = f"users/{body.sender_id}"
    params = {}
    user = Services.get(
        url,
        resource,
        params,
    )

    team = team_invitation.get("metadata", {}).get("team")

    notification = {
        "sender_id": body.sender_id,
        "receiver_id": body.receiver_id,
        "notification_type": "TEAM_INVITATION",
        "resource": "TEAM_INVITATIONS",
        "resource_id": team_invitation.get("tiid"),
        "metadata": {"user": user, "team": team},
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


@router.get("/notifications/", tags=["notifications"])
async def list_notifications(receiver_id: str):
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {"receiver_id": receiver_id}
    return Services.get(url, resource, params)


@router.put("/notifications/{nid}", tags=["notifications"])
async def put_notifications(nid: str, notification: NotificationUpdate):
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/" + nid
    params = {}
    return Services.put(url, resource, params, notification.to_json())


@router.put("/notifications/viewed/", tags=["notifications"])
async def put_notifications(nids: str):
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/viewed/"
    params = {"nids": nids}
    return Services.put(url, resource, params)


@router.post(
    "/notifications/team_postulation/", tags=["notifications"], status_code=201
)
async def create_team_postulation_to_project(
    body: TeamPostulation, x_tiger_token: Union[str, None] = Header(default=None)
):
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{body.tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{body.pid}"
    params = {}
    req_project = Services.get(url, resource, params, async_mode=True)

    team, project = Services.execute_many([req_team, req_project])

    team_owner = team.get("owner")
    token_user = Authenticator.get_user_id(x_tiger_token.replace("Bearer ", ""))
    project_owner = project.get("creator_uid")

    if team_owner != token_user and team.get("temporal") != True:
        raise HTTPException(
            status_code=401,
            detail="Only team owner can postulate his team to a project",
        )

    if team_owner == project_owner:
        raise HTTPException(
            status_code=401,
            detail="Project owner and team owner can't be the same person",
        )

    url = config.PROJECT_SERVICE_URL
    resource = f"projects/postulations/"
    params = {}
    response = Services.post(url, resource, params, body.to_json())

    notification = {
        "sender_id": body.tid,
        "receiver_id": response.get("project_owner_uid"),
        "notification_type": "TEAM_POSTULATION",
        "resource": "TEAM_POSTULATIONS",
        "resource_id": response.get("ppid"),
        "metadata": {"project": project, "team": team},
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


@router.post(
    "/notifications/team_postulation_response/", tags=["notifications"], status_code=201
)
async def create_team_postulation_response(body: TeamPostulationResponse):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/postulations/{body.ppid}"
    params = {}
    response = Services.put(url, resource, params, body.to_json())

    pid = response.get("pid")
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    req_project = Services.get(url, resource, params, async_mode=True)

    tid = response.get("tid")
    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    project, team = Services.execute_many([req_project, req_team])

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    if team.get("temporal"):
        for uid in team.get("members", []):
            notification = {
                "sender_id": response.get("project_owner_uid"),
                "receiver_id": uid,
                "notification_type": "TEAM_POSTULATION_RESPONSE",
                "resource": "TEAM_POSTULATIONS",
                "resource_id": response.get("ppid"),
                "metadata": {"response": body.state, "project": project},
            }
            Services.post(url, resource, params, notification)
        return {"message": "OK"}
    else:
        notification = {
            "sender_id": response.get("project_owner_uid"),
            "receiver_id": team.get("owner"),
            "notification_type": "TEAM_POSTULATION_RESPONSE",
            "resource": "TEAM_POSTULATIONS",
            "resource_id": response.get("ppid"),
            "metadata": {"response": body.state, "project": project},
        }

        return Services.post(url, resource, params, notification)


@router.post(
    "/notifications/project_finished/", tags=["notifications"], status_code=201
)
async def create_project_finished_notification(requests: ProjectRequests):
    pid = requests.pid
    tid = requests.tid

    url = config.PROJECT_SERVICE_URL
    resource = f"/project_finished_requests/{requests.request_id}"
    params = {}
    body = {"state": requests.state}
    Services.put(url, resource, params, body)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    team_req = Services.get(url, resource, params, async_mode=True)

    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    project_req = Services.get(url, resource, params, async_mode=True)
    team, project = Services.execute_many([team_req, project_req])

    notification = {
        "sender_id": team.get("tid"),
        "receiver_id": project.get("creator_uid"),
        "notification_type": "PROJECT_FINISHED",
        "resource": "PROJECTS",
        "resource_id": project.get("pid"),
        "metadata": {"project": project, "response": requests.state},
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


@router.post(
    "/notifications/project_finished_requests/", tags=["notifications"], status_code=201
)
async def create_project_finished_request_notification(requests: ProjectRequests):
    body = {"pid": requests.pid, "tid": requests.tid}

    url = config.PROJECT_SERVICE_URL
    resource = "/project_finished_requests/"
    params = {}
    result = Services.post(url, resource, params, body)

    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{requests.pid}"
    params = {}
    project = Services.get(url, resource, params)

    tid = project.get("team_assigned")

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    team = Services.get(url, resource, params)

    notification = {
        "sender_id": project.get("creator_uid"),
        "receiver_id": team.get("owner"),
        "notification_type": "PROJECT_FINISHED_REQUEST",
        "resource": "PROJECT_FINISHED_REQUESTS",
        "resource_id": result.get("pfr_id"),
        "metadata": {"project": project},
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


@router.post(
    "/notifications/project_abandonment/", tags=["notifications"], status_code=201
)
def create_abandoned_project_notification(project_abandonment: ProjectAbandonment):
    if project_abandonment.request_id is not None:
        url = config.PROJECT_SERVICE_URL
        resource = f"/project_abandons_requests/{project_abandonment.request_id}"
        params = {}
        body = {"state": project_abandonment.state}
        Services.put(url, resource, params, body)

    if (project_abandonment.state == RequestStates.ACCEPTED) or (
        project_abandonment.request_id is None and project_abandonment.state is None
    ):
        url = config.PROJECT_SERVICE_URL
        resource = "project_abandonment/"
        params = {}
        body_to_update = project_abandonment.to_json()
        if body_to_update.get("state", False):
            del body_to_update["state"]
        if body_to_update.get("request_id", False):
            del body_to_update["request_id"]

        Services.post(url, resource, params, body_to_update)

    pid = project_abandonment.pid
    tid = project_abandonment.tid

    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    req_project = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    project, team = Services.execute_many([req_project, req_team])

    notification = {
        "sender_id": team.get("tid"),
        "receiver_id": project.get("creator_uid"),
        "notification_type": "ABANDONED_PROJECT",
        "resource": "PROJECTS",
        "resource_id": project.get("pid"),
        "metadata": {
            "project": project,
            "team": team,
            "response": project_abandonment.state,
            "request_id": project_abandonment.request_id,
        },
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


@router.post(
    "/notifications/project_abandons_requests/", tags=["notifications"], status_code=201
)
def create_project_abandons_request_notification(
    project_abandons_requests: ProjectAbandonsRequests,
):
    url = config.PROJECT_SERVICE_URL
    resource = "project_abandons_requests/"
    params = {}
    project_abandons_requests_result = Services.post(
        url, resource, params, project_abandons_requests.to_json()
    )

    pid = project_abandons_requests_result.get("pid")
    tid = project_abandons_requests_result.get("tid")
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    req_project = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    project, team = Services.execute_many([req_project, req_team])

    notification = {
        "sender_id": project.get("creator_uid"),
        "receiver_id": team.get("owner"),
        "notification_type": "PROJECT_ABANDONS_REQUEST",
        "resource": "PROJECT_ABANDONS_REQUEST",
        "resource_id": project_abandons_requests_result.get("par_id"),
        "metadata": {"project": project, "team": team},
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


def send_team_review_notification(team, project):
    try:
        notifications_req = []
        members = team.get("members", [])

        for mid in members:
            if mid is not None:
                notification = {
                    "sender_id": team.get("owner"),
                    "receiver_id": mid,
                    "notification_type": "TEAM_REVIEW",
                    "resource": "TEAMS",
                    "resource_id": team.get("tid"),
                    "metadata": {"project": project, "team": team},
                }
                url = config.NOTIFICATION_SERVICE_URL
                resource = "notifications/"
                params = {}
                req = Services.post(
                    url, resource, params, notification, async_mode=True
                )
                notifications_req.append(req)

        if len(notifications_req) > 0:
            Services.execute_many(notifications_req)
    except Exception as e:
        print(f"error to send notifications for team review, e: {e}")


def send_new_candidate_notification(tpid, new_member_id):
    url = config.TEAM_SERVICE_URL
    resource = f"teams_positions/{tpid}"
    params = {}
    position = Services.get(url, resource, params)

    notification = {
        "sender_id": new_member_id,
        "receiver_id": position.get("team").get("owner"),
        "notification_type": "NEW_TEAM_CANDIDATE",
        "resource": "TEAMS_POSITIONS",
        "resource_id": tpid,
        "metadata": {"position": position},
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


def send_position_postulation_accepted_notification(tpid, new_member_id):
    url = config.TEAM_SERVICE_URL
    resource = f"teams_positions/{tpid}"
    params = {}
    position = Services.get(url, resource, params)

    notification = {
        "sender_id": position.get("team").get("owner"),
        "receiver_id": new_member_id,
        "notification_type": "TEAM_POSITION_ACCEPTED",
        "resource": "TEAMS",
        "resource_id": position.get("team").get("tid"),
        "metadata": {"position": position},
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


@router.post(
    "/notifications/project_invitation/", tags=["notifications"], status_code=201
)
async def send_project_invitation_notification(project_invitation: ProjectInvitation):
    pid = project_invitation.pid
    tid = project_invitation.tid
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    req_project = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    project, team = Services.execute_many([req_project, req_team])

    notification = {
        "sender_id": project.get("creator_uid"),
        "receiver_id": team.get("owner"),
        "notification_type": "PROJECT_INVITATION",
        "resource": "PROJECT",
        "resource_id": pid,
        "metadata": {"project": project, "team": team},
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


@router.post(
    "/notifications/teams_positions_invitations/",
    tags=["notifications"],
    status_code=201,
)
async def send_team_position_invitation_notification(
    position_invitation: PositionInvitation,
):
    uid = position_invitation.uid
    tpid = position_invitation.tpid

    url = config.TEAM_SERVICE_URL
    resource = f"teams_positions/{tpid}"
    params = {}
    team_position = Services.get(url, resource, params)

    notification = {
        "sender_id": team_position.get("tid"),
        "receiver_id": uid,
        "notification_type": "POSITION_INVITATION",
        "resource": "TEAMS_POSITIONS",
        "resource_id": tpid,
        "metadata": {"team_position": team_position},
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


def send_new_temporal_team_notification(uids, team):
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    for uid in uids:
        notification = {
            "sender_id": team.get("tid"),
            "receiver_id": uid,
            "notification_type": "NEW_TEMPORAL_TEAM",
            "resource": "TEAMS",
            "resource_id": team.get("tid"),
            "metadata": {"team": team},
        }
        Services.post(url, resource, params, notification)


def send_invitation_to_projects(uids, pid, team):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    project = Services.get(url, resource, params)

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    for uid in uids:
        notification = {
            "sender_id": project.get("creator_uid"),
            "receiver_id": uid,
            "notification_type": "PROJECT_INVITATION",
            "resource": "PROJECT",
            "resource_id": pid,
            "metadata": {"project": project, "team": team},
        }
        Services.post(url, resource, params, notification)


@router.post(
    "/notifications/teams_project_internal_recommendations/",
    tags=["notifications"],
    status_code=201,
)
async def send_project_internal_recommendation_notification(
    project_recommendation: TeamProjectInternalRecommendations,
):
    sender_id = project_recommendation.sender_id
    receiver_id = project_recommendation.receiver_id
    tid = project_recommendation.tid
    pid = project_recommendation.pid_recommendation

    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    project_req = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    url = config.USER_SERVICE_URL
    resource = f"users/{sender_id}"
    params = {}
    sender_req = Services.get(url, resource, params, async_mode=True)

    project, team, sender = Services.execute_many([project_req, req_team, sender_req])

    notification = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "notification_type": "TEAM_PROJECT_INTERNAL_RECOMMENDATION",
        "resource": "PROJECTS",
        "resource_id": pid,
        "metadata": {
            "team": team,
            "member": {"name": sender.get("name") + " " + sender.get("lastname")},
            "project": project,
        },
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)


@router.post(
    "/notifications/teams_member_internal_recommendations/",
    tags=["notifications"],
    status_code=201,
)
async def send_member_internal_recommendation_notification(
    project_recommendation: TeamMemberInternalRecommendations,
):
    sender_id = project_recommendation.sender_id
    receiver_id = project_recommendation.receiver_id
    tid = project_recommendation.tid
    uid = project_recommendation.uid_recommendation

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    url = config.USER_SERVICE_URL
    resource = f"users/{sender_id}"
    params = {}
    sender_req = Services.get(url, resource, params, async_mode=True)

    url = config.USER_SERVICE_URL
    resource = f"users/{uid}"
    params = {}
    user_req = Services.get(url, resource, params, async_mode=True)

    team, sender, user = Services.execute_many([req_team, sender_req, user_req])

    notification = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "notification_type": "TEAM_MEMBER_INTERNAL_RECOMMENDATION",
        "resource": "USERS",
        "resource_id": uid,
        "metadata": {
            "team": team,
            "member": {"name": sender.get("name") + " " + sender.get("lastname")},
            "user": {"name": user.get("name") + " " + user.get("lastname")},
        },
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)

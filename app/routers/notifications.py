from fastapi import APIRouter
from app import config
from app.models.requests.notifications.notification_update import NotificationUpdate
from app.models.requests.notifications.team_invitation import TeamInvitation
from app.models.requests.projects.team_postulation import TeamPostulation
from app.models.requests.projects.team_postulation_response import (
    TeamPostulationResponse,
)
from app.services import Services

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
async def create_team_postulation_to_project(body: TeamPostulation):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/postulations/"
    params = {}
    response = Services.post(url, resource, params, body.to_json())

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{body.tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{body.pid}"
    params = {}
    req_project = Services.get(url, resource, params, async_mode=True)

    team, project = Services.execute_many([req_team, req_project])

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

    notification = {
        "sender_id": response.get("project_owner_uid"),
        "receiver_id": team.get("owner"),
        "notification_type": "TEAM_POSTULATION_RESPONSE",
        "resource": "TEAM_POSTULATIONS",
        "resource_id": response.get("ppid"),
        "metadata": {"response": body.state, "project": project},
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)

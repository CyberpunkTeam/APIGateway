from fastapi import APIRouter
from app import config

from app.models.requests.notifications.notification_update import NotificationUpdate
from app.models.requests.notifications.team_invitation import TeamInvitation
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


@router.post(
    "/notifications/project_finished/", tags=["notifications"], status_code=201
)
async def create_project_finished_notification(requests: ProjectRequests):
    pid = requests.pid
    tid = requests.tid

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    team = Services.get(url, resource, params)

    url = config.PROJECT_SERVICE_URL
    resource = f"/project_finished_requests/{requests.request_id}"
    params = {}
    body = {"state": requests.state}
    Services.put(url, resource, params, body)

    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    project = Services.get(url, resource, params)
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
    project_abandonment_id = None
    if project_abandonment.request_id is not None:
        url = config.PROJECT_SERVICE_URL
        resource = f"/project_abandons_requests/{project_abandonment.request_id}"
        params = {}
        body = {"state": project_abandonment.state}
        Services.put(url, resource, params, body)

    if (project_abandonment.state == RequestStates.ACCEPTED) or (
        project_abandonment.request_id is not None and project_abandonment.state is None
    ):
        url = config.PROJECT_SERVICE_URL
        resource = "project_abandonment/"
        params = {}
        body_to_update = project_abandonment.to_json()
        if body_to_update.get("state", False):
            del body_to_update["state"]
        if body_to_update.get("request_id", False):
            del body_to_update["request_id"]

        project_abandonment_result = Services.post(
            url, resource, params, body_to_update
        )
        project_abandonment_id = project_abandonment_result.get("pa_id")

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
        "notification_type": "ABANDONED_PROJECT_REQUEST",
        "resource": "PROJECT_ABANDONS_REQUEST",
        "resource_id": project_abandons_requests_result.get("par_id"),
        "metadata": {"project": project, "team": team},
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    return Services.post(url, resource, params, notification)

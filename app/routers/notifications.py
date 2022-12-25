from fastapi import APIRouter
from app import config
from app.models.requests.notifications.notification_update import NotificationUpdate
from app.models.requests.notifications.team_invitation import TeamInvitation
from app.services import Services

router = APIRouter()


@router.post("/notifications/team_invitation/", tags=["notifications"], status_code=201)
async def create_notification(body: TeamInvitation):
    url = config.USER_SERVICE_URL
    resource = f"users/{body.sender_id}"
    params = {}
    req_user = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{body.tid}"
    params = {}
    req_team = Services.get(url, resource, params, async_mode=True)

    user, team = Services.execute_many([req_user, req_team])

    notification = {
        "sender_id": body.sender_id,
        "receiver_id": body.receiver_id,
        "notification_type": "TEAM_INVITATION",
        "resource": "TEAM",
        "resource_id": body.tid,
        "metadata": {"user": user, "team": team},
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}
    print(f"body_to send is {notification}")
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

from fastapi import APIRouter
from app import config
from app.models.requests.notifications.team_invitation import TeamInvitation
from app.services import Services

router = APIRouter()


@router.post("/notifications/team_invitation/", tags=["users"], status_code=201)
async def create_notification(body: TeamInvitation):
    notification = {
        "sender_id": body.sender_id,
        "receiver_id": body.receiver_id,
        "notification_type": "TEAM_INVITATION",
        "resource": "TEAM",
        "resource_id": body.tid,
    }
    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}
    return Services.post(url, resource, params, notification)


@router.get("/notifications/", tags=["users"])
async def list_notifications(receiver_id: str):
    url = config.USER_SERVICE_URL
    resource = "users/"
    params = {"receiver_id": receiver_id}
    return Services.get(url, resource, params)

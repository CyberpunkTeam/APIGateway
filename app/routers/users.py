from typing import Union

from fastapi import APIRouter, Header, HTTPException
from app import config
from app.models.requests.users.user_update import UserUpdate
from app.services import Services
from app.utils.authenticator import Authenticator

router = APIRouter()


@router.post("/users/", tags=["users"], status_code=201)
async def create_user(body: dict):
    url = config.USER_SERVICE_URL
    resource = "users/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/users/", tags=["users"])
async def list_users():
    url = config.USER_SERVICE_URL
    resource = "users/"
    params = {}
    return Services.get(url, resource, params)


@router.get("/users/{user_id}", tags=["users"])
async def read_user(user_id: str):
    url = config.USER_SERVICE_URL
    resource = f"users/{user_id}"
    params = {}
    return Services.get(url, resource, params)


@router.put("/users/{user_id}", tags=["users"])
async def put_user(
    user_id: str,
    user_update: UserUpdate,
    x_tiger_token: Union[str, None] = Header(default=None),
):
    token_user = Authenticator.get_user_id(x_tiger_token.replace("Bearer ", ""))

    if user_id != token_user:
        raise HTTPException(
            status_code=401,
            detail="Not authorization for user updating ",
        )

    url = config.USER_SERVICE_URL
    resource = f"users/{user_id}"
    params = {}
    return Services.put(url, resource, params, user_update.to_json())


@router.post("/users/{follower_uid}/following/{uid}", tags=["users"])
async def add_follower_to_user(uid: str, follower_uid: str):
    url = config.USER_SERVICE_URL
    resource = f"/users/{uid}/followers/{follower_uid}"
    params = {}
    result = Services.post(url, resource, params)

    url = config.USER_SERVICE_URL
    resource = f"users/{follower_uid}"
    params = {}
    user = Services.get(url, resource, params)

    notification = {
        "sender_id": follower_uid,
        "receiver_id": uid,
        "notification_type": "NEW_FOLLOWER",
        "resource": "USERS",
        "resource_id": follower_uid,
        "metadata": {
            "follower_name": f"{user['name']} {user['lastname']}",
            "following_tyoe": "user",
        },
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    Services.post(url, resource, params, notification)

    return result


@router.post("/users/teams/{follower_uid}/following/{tid}", tags=["users"])
async def add_follower_to_team(tid: str, follower_uid: str):
    url = config.USER_SERVICE_URL
    resource = f"/users/teams/{tid}/followers/{follower_uid}"
    params = {}
    result = Services.post(url, resource, params)

    url = config.TEAM_SERVICE_URL
    resource = f"teams/{tid}"
    params = {}
    team_req = Services.get(url, resource, params, async_mode=True)

    url = config.USER_SERVICE_URL
    resource = f"users/{follower_uid}"
    params = {}
    user_req = Services.get(url, resource, params, async_mode=True)

    team, user = Services.execute_many([team_req, user_req])

    notification = {
        "sender_id": follower_uid,
        "receiver_id": team.get("owner"),
        "notification_type": "NEW_FOLLOWER",
        "resource": "USERS",
        "resource_id": follower_uid,
        "metadata": {
            "follower_name": f"{user['name']} {user['lastname']}",
            "following_type": "team",
            "following_team_name": team.get("name"),
        },
    }

    url = config.NOTIFICATION_SERVICE_URL
    resource = "notifications/"
    params = {}

    Services.post(url, resource, params, notification)

    return result

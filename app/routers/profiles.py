import asyncio

from fastapi import APIRouter
from app import config
from app.services import Services

router = APIRouter()


@router.get("/profiles/{user_id}", tags=["profiles"], status_code=200)
async def get_profile(user_id: str):
    try:
        url = config.USER_SERVICE_URL
        resource = f"users/{user_id}"
        params = {}
        user_data = Services.get(url, resource, params)
    except:
        user_data = {"error": "internal error"}

    try:
        url = config.TEAM_SERVICE_URL
        resource = "teams/"
        params = {"mid": user_id}
        team_data = Services.get(url, resource, params)
    except:
        team_data = {}

    try:
        url = config.PROJECT_SERVICE_URL
        resource = "projects/"
        params = {"creator_uid": user_id}
        projects = Services.get(url, resource, params)

    except:
        projects = {}

    return {"user": user_data, "teams": team_data, "projects": projects}

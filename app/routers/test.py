from fastapi import APIRouter
from app import config
from app.services import Services

router = APIRouter()


@router.get("/tests/users/", tags=["users"])
async def list_users():
    url = config.INTERNAL_USER_SERVICE_URL
    resource = "users/"
    params = {}
    return Services.get(url, resource, params)


@router.get("/tests/ping/", tags=["users"])
async def list_users():
    url = config.INTERNAL_USER_SERVICE_URL
    resource = ""
    params = {}
    return Services.get(url, resource, params)

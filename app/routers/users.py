from fastapi import APIRouter
from app import config
from app.services import Services

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

from fastapi import APIRouter, HTTPException

from app import config
from app.models.entity import Entity
from app.services import Services

router = APIRouter()


@router.get("/searches/{entity}", tags=["searches"])
async def search(entity: Entity = None, word: str = ""):
    if word == "":
        raise HTTPException(status_code=400, detail="Word must not be empty")

    result = {}
    if entity == Entity.USERS:
        url = config.USER_SERVICE_URL
        resource = f"users/"
        params = {"search": word}
        users = Services.get(url, resource, params)
        result["users"] = users

    return result

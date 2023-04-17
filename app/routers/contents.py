from fastapi import APIRouter
from app.services import Services
from app import config

router = APIRouter()


@router.post("/contents/", tags=["contents"], status_code=201)
async def create_content(body: dict):
    url = config.CONTENT_SERVICE_URL
    resource = "contents/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/contents/", tags=["contents"], status_code=200)
async def get_contents(author_uid: str = None, tid: str = None):
    url = config.CONTENT_SERVICE_URL
    resource = "contents/"
    params = {}
    if author_uid is not None:
        params["author_uid"] = author_uid
    if tid is not None:
        params["tid"] = tid

    return Services.get(url, resource, params)


@router.get("/contents/{cid}", tags=["contents"], status_code=200)
async def get_contents(cid: str = None):
    url = config.CONTENT_SERVICE_URL
    resource = f"contents/{cid}"
    params = {}

    return Services.get(url, resource, params)

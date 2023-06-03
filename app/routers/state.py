from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["state"])
async def ping():
    return "pong"

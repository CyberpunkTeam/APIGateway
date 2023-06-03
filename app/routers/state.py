from fastapi import APIRouter

from app import config
from app.utils.tracks_repository import TracksRepository

router = APIRouter()


@router.get("/", tags=["state"])
async def ping():
    tracks_repository = TracksRepository(config.DATABASE_URL, config.DATABASE_NAME)
    tracks = tracks_repository.get()
    return tracks

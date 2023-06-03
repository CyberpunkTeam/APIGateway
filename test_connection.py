from app import config
from app.utils.tracks import Tracks
from app.utils.tracks_repository import TracksRepository

tracks_repository = TracksRepository(config.DATABASE_URL, config.DATABASE_NAME)

tracks = tracks_repository.insert_many(
    [Tracks(uid="test", path="/test", created_date="test")]
)

print(tracks)

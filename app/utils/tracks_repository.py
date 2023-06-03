from cpunk_mongo.db import DataBase

from app.utils.tracks import Tracks


class TracksRepository(DataBase):
    COLLECTION_NAME = "tracks"

    def __init__(self, url, db_name):
        if db_name == "test":
            import mongomock

            self.db = mongomock.MongoClient().db
        else:
            super().__init__(url, db_name)

    def get(self):
        return self.filter(self.COLLECTION_NAME, {}, output_model=Tracks)

    def insert_many(self, tracks: Tracks):
        return self.save_many(self.COLLECTION_NAME, tracks)

from datetime import datetime

from app import config
from app.models.requests.metrics import Tracks
from app.services import Services


class SessionsManager:
    def __init__(self):
        self.users_loaded = {}
        self.new_sessions = {}
        self.date = datetime.now().strftime("%d-%m-%Y")
        self.last_updated = datetime.now()

    def batch_load_session(self):
        try:
            current_datetime = datetime.now()
            if (current_datetime - self.last_updated).seconds > 60:

                self.last_updated = current_datetime
                tracks = []
                for uid, timestamp in self.new_sessions.items():
                    tracks.append(
                        Tracks(
                            uid=uid, path="/session", created_date=timestamp
                        ).to_json()
                    )

                if len(tracks) > 0:
                    url = config.METRIC_SERVICE_URL
                    resource = "tracks/"
                    params = {}
                    Services.post(url, resource, params, tracks)

                self.users_loaded.update(self.new_sessions)
                self.new_sessions = {}

            current_date = datetime.now().strftime("%d-%m-%Y")
            if current_date != self.date:
                self.users_loaded = {}
                self.date = current_date
        except Exception as e:
            print("tracking error: ", e)

    def add_user(self, uid):
        if uid not in self.users_loaded:
            self.new_sessions[uid] = datetime.now().strftime("%d-%m-%Y")
        self.batch_load_session()

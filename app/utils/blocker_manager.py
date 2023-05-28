from datetime import datetime, timedelta

from app import config
from app.models.requests.states import States
from app.services import Services


class BlockerManager:
    def __init__(self):
        self.blocked_users = []
        self.last_update = datetime.now()

    def is_blocked_user(self, uid):
        current_time = datetime.now()
        if self.last_update + timedelta(minutes=1) < current_time:
            self._update_blocked_user()
            self.last_update = current_time
        return uid in self.blocked_users

    def _update_blocked_user(self):
        url = config.USER_SERVICE_URL
        resource = "users/"
        params = {"state": States.BLOCKED}
        users = Services.get(url, resource, params)
        self.blocked_users = [user.get("uid") for user in users]

import firebase_admin
from firebase_admin import auth, credentials

import os


class GoogleAuth:
    def __init__(self):
        path = os.path.dirname(__file__)
        path_list = path.split("/")
        path_file = "/".join(path_list[: len(path_list) - 2])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path_file + "/credentials.json"
        firebase_admin.initialize_app()

    def valid_token(self, token):
        try:
            auth.verify_id_token(token)
            return True
        except:
            return False

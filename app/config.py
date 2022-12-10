# ENV VARS, CONSTANTS
import os

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://test.com/")
INTERNAL_USER_SERVICE_URL = os.environ.get(
    "INTERNAL_USER_SERVICE_URL", "http://test.com/"
)
TEAM_SERVICE_URL = os.environ.get("TEAM_SERVICE_URL", "http://test.com/")

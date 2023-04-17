# ENV VARS, CONSTANTS
import os

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://test.com/")
TEAM_SERVICE_URL = os.environ.get("TEAM_SERVICE_URL", "http://test.com/")
NOTIFICATION_SERVICE_URL = os.environ.get(
    "NOTIFICATION_SERVICE_URL", "http://test.com/"
)
PROJECT_SERVICE_URL = os.environ.get("PROJECT_SERVICE_URL", "http://test.com/")
RECOMMENDATION_SERVICE_URL = os.environ.get(
    "RECOMMENDATION_SERVICE_URL", "http://test.com/"
)
CONTENT_SERVICE_URL = os.environ.get("CONTENT_SERVICE_URL", "http://test.com/")

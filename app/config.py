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
METRIC_SERVICE_URL = os.environ.get("METRIC_SERVICE_URL", "http://test.com/")


DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

DATABASE_URL = os.environ.get("DATABASE_URL", "server.example.com")
if DATABASE_USER is not None and DATABASE_PASSWORD is not None:
    DATABASE_URL = f"mongodb+srv://{DATABASE_USER}:{DATABASE_PASSWORD}@findmyteam.slcsp0t.mongodb.net/?retryWrites=true&w=majority"


DATABASE_NAME = os.environ.get("DATABASE_NAME", "test")

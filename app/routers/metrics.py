from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter

from app import config
from app.models.requests.metrics import Tracks
from app.services import Services

router = APIRouter()


@router.post("/tracks/", tags=["metrics"], status_code=201)
async def create_tracks(body: List[Tracks]):
    url = config.METRIC_SERVICE_URL
    resource = "tracks/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/metrics", tags=["metrics"])
async def get_metrics(days: int = -1):
    url_projects = config.PROJECT_SERVICE_URL
    url_teams = config.TEAM_SERVICE_URL
    url_users = config.USER_SERVICE_URL
    url_metrics = config.METRIC_SERVICE_URL
    resource = "metrics"
    params = {}

    projects_req = Services.get(url_projects, resource, params, async_mode=True)
    teams_req = Services.get(url_teams, resource, params, async_mode=True)
    users_req = Services.get(url_users, resource, params, async_mode=True)
    metrics_req = Services.get(url_metrics, resource, params, async_mode=True)

    projects, teams, users, sessions = Services.execute_many(
        [projects_req, teams_req, users_req, metrics_req]
    )

    if days != -1:

        min_date = (datetime.now() - timedelta(days)).strftime("%Y-%m-%d")

        input_labels = projects.get("projects_created").get("labels")
        input_values = projects.get("projects_created").get("values")
        labels, values = filter_dates(input_labels, input_values, min_date)

        projects["projects_created"] = {"labels": labels, "values": values}

        input_labels = teams.get("teams_created").get("labels")
        input_values = teams.get("teams_created").get("values")
        labels, values = filter_dates(input_labels, input_values, min_date)

        teams["teams_created"] = {"labels": labels, "values": values}

        input_labels = users.get("users_created").get("labels")
        input_values = users.get("users_created").get("values")
        labels, values = filter_dates(input_labels, input_values, min_date)

        users["users_created"] = {"labels": labels, "values": values}

    result = {
        "projects": projects,
        "teams": teams,
        "users": users,
        "sessions": sessions,
    }

    return result


def _get_date_to_compare(date):
    date_list = date.split("-")
    day = date_list[0]
    month = date_list[1]
    year = date_list[2]
    return f"{year}-{month}-{day}"


def filter_dates(labels, values, min_date):
    new_labels = []
    new_values = []
    for i in range(len(labels)):
        date = labels[i]
        if _get_date_to_compare(date) >= min_date:
            new_labels.append(date)
            new_values.append(values[i])
    return new_labels, new_values

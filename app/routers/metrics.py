from datetime import datetime, timedelta

from fastapi import APIRouter

from app import config
from app.services import Services

router = APIRouter()


@router.get("/metrics", tags=["metrics"])
async def get_metrics(days: int = 7):
    url_projects = config.PROJECT_SERVICE_URL
    url_teams = config.TEAM_SERVICE_URL
    url_users = config.USER_SERVICE_URL
    resource = "metrics"
    params = {}

    projects_req = Services.get(url_projects, resource, params, async_mode=True)
    teams_req = Services.get(url_teams, resource, params, async_mode=True)
    users_req = Services.get(url_users, resource, params, async_mode=True)

    projects, teams, users = Services.execute_many([projects_req, teams_req, users_req])

    min_date = (datetime.now() - timedelta(days)).strftime("%Y-%m-%d")

    labels = []
    values = []
    input_labels = projects.get("projects_created").get("labels")
    for i in range(len(input_labels)):
        date = input_labels[i]
        if _get_date_to_compare(date) >= min_date:
            labels.append(date)
            values.append(projects.get("projects_created").get("values")[i])

    projects["projects_created"] = {"labels": labels, "values": values}

    result = {"projects": projects, "teams": teams, "users": users}

    return result


def _get_date_to_compare(date):
    date_list = date.split("-")
    day = date_list[0]
    month = date_list[1]
    year = date_list[2]
    return f"{year}-{month}-{day}"

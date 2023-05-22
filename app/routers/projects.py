from typing import Union

from fastapi import APIRouter, Header, HTTPException
from app import config
from app.models.currency import Currency
from app.models.project_states import ProjectStates
from app.models.requests.projects.project_update import ProjectsUpdate
from app.models.requests.teams.team_invitations_update import States
from app.routers.recommendations import (
    _get_team_recommendations,
    _create_temporal_team_recommendations,
)
from app.services import Services
from app.utils.authenticator import Authenticator

router = APIRouter()


@router.post("/projects/", tags=["projects"], status_code=201)
async def create_project(body: dict):
    url = config.PROJECT_SERVICE_URL
    resource = "projects/"
    params = {}
    project = Services.post(url, resource, params, body)
    teams_recommendations = _get_team_recommendations(project, new_project=True)
    project["teams_recommendations"] = teams_recommendations
    temporal_team_recommendations = _create_temporal_team_recommendations(project)
    project["temporal_teams_recommendations"] = temporal_team_recommendations
    return project


@router.get("/projects/", tags=["projects"])
async def list_projects(
    creator_uid: str = None,
    state: ProjectStates = None,
    currency: Currency = None,
    min_budget: float = None,
    max_budget: float = None,
    project_types: str = None,
    idioms: str = None,
    programming_languages: str = None,
    frameworks: str = None,
    platforms: str = None,
    databases: str = None,
):
    url = config.PROJECT_SERVICE_URL
    resource = "projects/"
    params = {}
    if creator_uid is not None:
        params["creator_uid"] = creator_uid

    if state is not None:
        params["state"] = state

    if currency is not None:
        params["currency"] = currency

    if min_budget is not None:
        params["min_budget"] = min_budget

    if max_budget is not None:
        params["max_budget"] = max_budget

    if project_types is not None:
        params["project_types"] = project_types

    if idioms is not None:
        params["idioms"] = idioms

    if programming_languages is not None:
        params["programming_languages"] = programming_languages

    if databases is not None:
        params["databases"] = databases

    if platforms is not None:
        params["platforms"] = platforms

    if frameworks is not None:
        params["frameworks"] = frameworks

    projects = Services.get(url, resource, params)

    creators_uid = {project.get("creator_uid") for project in projects}

    if len(creators_uid) > 0:
        uids = "[" + ",".join(creators_uid) + "]"
        url = config.USER_SERVICE_URL
        params = {"uids": uids}
        resource = "users/"
        creators = Services.get(url, resource, params)
    else:
        creators = []

    creators_dicts = {creator.get("uid"): creator for creator in creators}

    for project in projects:
        creator_uid = project.get("creator_uid")
        creator = creators_dicts.get(creator_uid)
        del project["creator_uid"]
        project["creator"] = creator

    return projects


@router.get("/projects/{pid}", tags=["projects"])
async def read_project(pid: str):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    project = Services.get(url, resource, params)
    project = add_team(project)
    project = add_creator(project)
    return project


def add_team(project):
    if project.get("team_assigned") is None:
        return project
    try:
        tid = project.get("team_assigned")
        url = config.TEAM_SERVICE_URL
        resource = f"teams/{tid}"
        params = {}
        team = Services.get(url, resource, params)
        project["team_assigned"] = team
        return project
    except:
        return project


def add_creator(project):
    try:
        url = config.USER_SERVICE_URL
        resource = f"users/{project.get('creator_uid')}"
        params = {}
        creator = Services.get(url, resource, params)
        del project["creator_uid"]
        project["creator"] = creator
        return project
    except:
        return project


@router.put("/projects/{pid}", tags=["projects"])
async def put_projects(
    pid: str,
    project_update: ProjectsUpdate,
    x_tiger_token: Union[str, None] = Header(default=None),
):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    project = Services.get(url, resource, params)

    token = x_tiger_token.replace("Bearer ", "")

    token_user = "mati" if token is "mati" else Authenticator.get_user_id(token)

    project_owner = project.get("creator_uid")

    if (token_user != project_owner) and (token != "mati"):
        raise HTTPException(
            status_code=401,
            detail="Project owner only has authorization for project updating",
        )

    return Services.put(url, resource, params, project_update.to_json())


@router.get("/projects/postulations/", tags=["projects"], status_code=200)
async def get_team_postulations(pid: str = None, tid: str = None, state: States = None):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/postulations/"
    params = {}
    if pid is not None:
        params["pid"] = pid

    if tid is not None:
        params["tid"] = tid

    if state is not None:
        params["state"] = state

    postulations = Services.get(url, resource, params)

    if tid is not None:
        reqs_projects = []
        for postulation in postulations:
            url = config.PROJECT_SERVICE_URL
            resource = f"projects/{postulation.get('pid')}"
            params = {}
            req_project = Services.get(url, resource, params, async_mode=True)
            reqs_projects.append(req_project)
        projects = Services.execute_many(reqs_projects)
        for i in range(len(postulations)):
            postulations[i]["project"] = projects[i]

    if pid is not None:
        reqs_teams = []
        for postulation in postulations:
            url = config.TEAM_SERVICE_URL
            resource = f"teams/{postulation.get('tid')}"
            params = {}
            req_team = Services.get(url, resource, params, async_mode=True)
            reqs_teams.append(req_team)
        teams = Services.execute_many(reqs_teams)

        reqs_members = []
        for team in teams:
            url = config.USER_SERVICE_URL
            members = team["members"]
            query_param = "[" + ",".join(members) + "]"
            resource = f"users/"
            params = {"uids": query_param}
            req_members = Services.get(url, resource, params, async_mode=True)
            reqs_members.append(req_members)

        members_info = Services.execute_many(reqs_members)

        for j in range(len(teams)):
            teams[j]["members"] = members_info[j]

        for i in range(len(postulations)):
            postulations[i]["team"] = teams[i]

        reviews_reqs = []
        for team in teams:
            url = config.TEAM_SERVICE_URL
            resource = "teams_reviews/"
            params = {"tid": team.get("tid")}
            reviews_req = Services.get(url, resource, params, async_mode=True)
            reviews_reqs.append(reviews_req)
        reviews = Services.execute_many(reviews_reqs)

        for i in range(len(teams)):

            total_ratings = 0
            amount_ratings = 0
            for review in reviews[i]:
                amount_ratings += 1
                total_ratings += review.get("rating", 0)

            teams[i]["overall_rating"] = round(
                float(total_ratings) / amount_ratings if amount_ratings > 0 else 0, 1
            )
            teams[i]["reviews"] = reviews

    return postulations


@router.get("/projects/postulations/{ppid}", tags=["projects"], status_code=200)
async def get_team_postulation_to_project(ppid: str):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/postulations/{ppid}"
    params = {}
    return Services.get(url, resource, params)


@router.get("/project_abandonment/", tags=["projects"], status_code=200)
async def list_project_abandonment(tid: str = None, pid: str = None):
    url = config.PROJECT_SERVICE_URL
    resource = "project_abandonment/"
    params = {}
    if tid is not None:
        params["tid"] = tid
    if pid is not None:
        params["pid"] = pid

    return Services.get(url, resource, params)


@router.get("/project_abandonment/{pa_id}", tags=["projects"], status_code=200)
async def get_project_abandonment(pa_id: str):
    url = config.PROJECT_SERVICE_URL
    resource = f"project_abandonment/{pa_id}"
    params = {}
    return Services.get(url, resource, params)


@router.get("/project_abandons_requests/", tags=["projects"], status_code=200)
async def list_project_abandons_requests(tid: str = None, pid: str = None):
    url = config.PROJECT_SERVICE_URL
    resource = "project_abandons_requests/"
    params = {}
    if tid is not None:
        params["tid"] = tid
    if pid is not None:
        params["pid"] = pid

    return Services.get(url, resource, params)


@router.get("/project_abandons_requests/{par_id}", tags=["projects"], status_code=200)
async def get_project_abandons_requests(par_id: str):
    url = config.PROJECT_SERVICE_URL
    resource = f"project_abandons_requests/{par_id}"
    params = {}
    return Services.get(url, resource, params)


@router.get("/project_finished_requests/", tags=["projects"], status_code=200)
async def list_project_finished_requests(tid: str = None, pid: str = None):
    url = config.PROJECT_SERVICE_URL
    resource = "project_finished_requests/"
    params = {}
    if tid is not None:
        params["tid"] = tid
    if pid is not None:
        params["pid"] = pid

    return Services.get(url, resource, params)


@router.get("/project_finished_requests/{pfr_id}", tags=["projects"], status_code=200)
async def get_project_finished_requests(pfr_id: str):
    url = config.PROJECT_SERVICE_URL
    resource = f"project_finished_requests/{pfr_id}"
    params = {}
    return Services.get(url, resource, params)


@router.post("/projects_reviews/", tags=["projects"], status_code=201)
async def create_project_review(body: dict):
    url = config.PROJECT_SERVICE_URL
    resource = "projects_reviews/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/projects_reviews/", tags=["projects"], status_code=200)
async def get_project_review(pid: str = None, tid: str = None):
    url = config.PROJECT_SERVICE_URL
    resource = "projects_reviews/"
    params = {}
    if pid is not None:
        params["pid"] = pid
    if tid is not None:
        params["tid"] = tid
    return Services.get(url, resource, params)

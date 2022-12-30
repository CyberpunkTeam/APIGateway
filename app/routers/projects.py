from fastapi import APIRouter
from app import config
from app.models.requests.projects.project_update import ProjectsUpdate
from app.models.requests.teams.team_invitations_update import States
from app.services import Services

router = APIRouter()


@router.post("/projects/", tags=["projects"], status_code=201)
async def create_project(body: dict):
    url = config.PROJECT_SERVICE_URL
    resource = "projects/"
    params = {}
    return Services.post(url, resource, params, body)


@router.get("/projects/", tags=["projects"])
async def list_projects(creator_uid: str = None):
    url = config.PROJECT_SERVICE_URL
    resource = "projects/"
    params = {}
    if creator_uid is not None:
        params["creator_uid"] = creator_uid
    projects = Services.get(url, resource, params)
    return list(map(add_creator, projects))


@router.get("/projects/{pid}", tags=["projects"])
async def read_project(pid: str):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    project = Services.get(url, resource, params)
    project = add_creator(project)
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
async def put_projects(pid: str, project_update: ProjectsUpdate):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/{pid}"
    params = {}
    return Services.put(url, resource, params, project_update.to_json())


@router.get("/projects/postulations/", tags=["projects"], status_code=200)
async def get_team_postulation_to_project(
    pid: str = None, tid: str = None, state: States = None
):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/postulations/"
    params = {}
    if pid is not None:
        params["pid"] = pid

    if tid is not None:
        params["tid"] = tid

    if state is not None:
        params["state"] = state

    return Services.get(url, resource, params)


@router.get("/projects/postulations/{ppid}", tags=["projects"], status_code=200)
async def get_team_postulation_to_project(ppid: str):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/postulations/{ppid}"
    params = {}
    return Services.get(url, resource, params)

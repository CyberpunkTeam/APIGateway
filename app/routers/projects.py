from fastapi import APIRouter
from app import config
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

    return project


def add_creator(project):
    try:
        url = config.USER_SERVICE_URL
        resource = f"users/{project.get('creator_uid')}"
        params = {}
        creator = Services.get(url, resource, params)
        del project["creator_uid"]
        project["creator"] = creator
    except:
        pass

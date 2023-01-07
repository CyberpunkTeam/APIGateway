from fastapi import APIRouter
from app import config
from app.models.project_states import ProjectStates
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
async def list_projects(creator_uid: str = None, state: ProjectStates = None):
    url = config.PROJECT_SERVICE_URL
    resource = "projects/"
    params = {}
    if creator_uid is not None:
        params["creator_uid"] = creator_uid

    if state is not None:
        params["state"] = state

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

    return postulations


@router.get("/projects/postulations/{ppid}", tags=["projects"], status_code=200)
async def get_team_postulation_to_project(ppid: str):
    url = config.PROJECT_SERVICE_URL
    resource = f"projects/postulations/{ppid}"
    params = {}
    return Services.get(url, resource, params)

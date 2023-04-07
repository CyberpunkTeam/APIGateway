from fastapi import APIRouter

from app import config
from app.routers.teams import _get_team
from app.services import Services

router = APIRouter()


@router.post("/recommendations/projects/", tags=["recommendations"], status_code=201)
async def create_team_recommendations(project: dict):
    return _get_team_recommendations(project)


def _get_team_recommendations(project, new_project=False):
    url = config.RECOMMENDATION_SERVICE_URL
    resource = "recommendations/projects/"
    params = {}
    tids = Services.post(url, resource, params, project)

    teams = [_get_team(tid) for tid in tids]
    teams = list(
        filter(
            lambda team: team.get("owner") != project.get("creator", {}).get("uid"),
            teams,
        )
    )

    teams = list(
        sorted(teams, key=lambda team: team.get("overall_rating"), reverse=True)
    )

    teams = teams[:5]
    if not new_project:
        requests_not = []
        for team in teams:
            receiver_id = team.get("owner")
            sender_id = project.get("creator", {}).get("uid")
            resource_id = project.get("pid")

            url = config.NOTIFICATION_SERVICE_URL
            resource = "notifications/"
            params = {
                "receiver_id": receiver_id,
                "sender_id": sender_id,
                "resource_id": resource_id,
            }
            req = Services.get(url, resource, params, async_mode=True)
            requests_not.append(req)
        notifications = Services.execute_many(requests_not)

        for i in range(len(notifications)):
            notification_list = notifications[i]
            teams[i]["sent_notification"] = len(notification_list) > 0

    return teams


@router.post(
    "/recommendations/models/{recommender_name}",
    tags=["recommendations"],
    status_code=201,
)
async def create_team_recommendations(recommender_name: str):
    url = config.RECOMMENDATION_SERVICE_URL
    resource = f"/recommendations/models/{recommender_name}/training"
    params = {}
    return Services.post(url, resource, params, {})


@router.post("/recommendations/users/", tags=["recommendations"], status_code=201)
async def create_team_recommendations(user: dict):
    url = config.RECOMMENDATION_SERVICE_URL
    resource = "recommendations/users/"
    params = {}
    tpids = Services.post(url, resource, params, user)

    reqs = []
    for tpid in tpids:
        url = config.TEAM_SERVICE_URL
        resource = f"teams_positions/{tpid}"
        params = {}

        reqs.append(Services.get(url, resource, params, async_mode=True))

    results = Services.execute_many(reqs)

    results = list(
        filter(
            lambda position: position.get("team").get("owner") != user.get("uid"),
            results,
        )
    )

    return results


@router.post(
    "/recommendations/teams_positions/", tags=["recommendations"], status_code=201
)
async def create_team_recommendations(team_position: dict):
    url = config.RECOMMENDATION_SERVICE_URL
    resource = "recommendations/teams_positions/"
    params = {}
    uids = Services.post(url, resource, params, team_position)

    members = team_position.get("team", {}).get("members", [])
    uids = [uid for uid in uids if not (uid in members)]

    reqs = []
    for uid in uids:
        url = config.USER_SERVICE_URL
        resource = f"users/{uid}"
        reqs.append(Services.get(url, resource, params, async_mode=True))

    results = Services.execute_many(reqs)

    return results


@router.post(
    "/recommendations/temporal_teams/", tags=["recommendations"], status_code=201
)
async def create_team_recommendations(project: dict):
    url = config.RECOMMENDATION_SERVICE_URL
    resource = "recommendations/temporal_team/"
    params = {}
    uids = Services.post(url, resource, params, project)

    reqs = []
    for uid in uids:
        url = config.USER_SERVICE_URL
        resource = f"users/{uid}"
        reqs.append(Services.get(url, resource, params, async_mode=True))

    users = Services.execute_many(reqs)

    members_3 = users[:3]
    skills_3 = get_team_skills(members_3)
    team_3 = {
        "name": f"Temporal team - Small - {project.get('name')}",
        "members": members_3,
        "skills": skills_3,
    }

    if len(users) < 3:
        return [team_3]

    members_5 = users[:5]
    skills_5 = get_team_skills(members_5)
    team_5 = {
        "name": f"Temporal team - Large - {project.get('name')}",
        "members": members_5,
        "skills": skills_5,
    }

    return [team_3, team_5]


def get_team_skills(users):
    programming_language = set()
    frameworks = set()
    platforms = set()
    databases = set()
    for user in users:
        user_skills = user.get("skills", {})

        user_programming_language = user_skills.get("programming_language", [])
        for programming_language_i in user_programming_language:
            programming_language.add(programming_language_i)

        user_frameworks = user_skills.get("frameworks", [])
        for frameworks_i in user_frameworks:
            frameworks.add(frameworks_i)

        user_platforms = user_skills.get("platforms", [])
        for platforms_i in user_platforms:
            platforms.add(platforms_i)

        user_databases = user_skills.get("databases", [])
        for databases_i in user_databases:
            databases.add(databases_i)

    return {
        "programming_language": list(programming_language),
        "frameworks": list(frameworks),
        "platforms": list(platforms),
        "databases": list(databases),
    }

from fastapi import APIRouter
from app import config
from app.services import Services

router = APIRouter()


@router.get("/profiles/{user_id}", tags=["profiles"], status_code=200)
async def get_profile(user_id: str):
    url = config.USER_SERVICE_URL
    resource = f"users/{user_id}"
    params = {}
    req_user_data = Services.get(url, resource, params, async_mode=True)

    url = config.TEAM_SERVICE_URL
    resource = "teams/"
    params = {"mid": user_id}
    req_team_data = Services.get(url, resource, params, async_mode=True)

    url = config.PROJECT_SERVICE_URL
    resource = "projects/"
    params = {"creator_uid": user_id}
    req_projects = Services.get(url, resource, params, async_mode=True)

    user_data, team_data, projects = Services.execute_many(
        [req_user_data, req_team_data, req_projects]
    )

    reviews_reqs = []
    for team in team_data:
        url = config.PROJECT_SERVICE_URL
        resource = "projects_reviews/"
        params = {"tid": team.get("tid")}
        reviews_req = Services.get(url, resource, params, async_mode=True)
        reviews_reqs.append(reviews_req)
    reviews = Services.execute_many(reviews_reqs)

    for i in range(len(team_data)):

        total_ratings = 0
        amount_ratings = 0
        for review in reviews[i]:
            amount_ratings += 1
            total_ratings += review.get("rating", 0)

        team_data[i]["overall_rating"] = round(
            float(total_ratings) / amount_ratings if amount_ratings > 0 else 0, 1
        )
        team_data[i]["reviews"] = reviews

    return {"user": user_data, "teams": team_data, "projects": projects}

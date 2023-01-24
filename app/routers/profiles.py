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

    url = config.PROJECT_SERVICE_URL
    resource = "projects_reviews/"
    params = {"tid": team_data.get("tid")}
    reviews = Services.get(url, resource, params)

    total_ratings = 0
    amount_ratings = 0
    for review in reviews:
        amount_ratings += 1
        total_ratings += review.get("rating", 0)

    team_data["overall_rating"] = round(
        float(total_ratings) / amount_ratings if amount_ratings > 0 else 0, 1
    )
    team_data["reviews"] = reviews

    return {"user": user_data, "teams": team_data, "projects": projects}

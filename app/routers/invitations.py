from fastapi import APIRouter, HTTPException
from app import config
from app.models.requests.teams.team_invitations_update import (
    TeamInvitationUpdate,
    States,
)
from app.services import Services

router = APIRouter()


@router.get("/invitations/teams/", tags=["invitations"], status_code=201)
async def get_teams_invitations(
    tid: str = None, postulant_uid: str = None, state: str = None
):
    url = config.TEAM_SERVICE_URL
    resource = f"/team_invitations/"
    params = {}

    if state is not None:
        params["state"] = state

    if tid is not None:
        params["tid"] = tid
        invitations = Services.get(url, resource, params)
        reqs_get_users = []
        for invitation in invitations:
            uid = invitation.get("postulant_uid")
            url = config.USER_SERVICE_URL
            resource = f"users/{uid}"
            params = {}
            req_get_user = Services.get(url, resource, params, async_mode=True)
            reqs_get_users.append(req_get_user)

        responses = Services.execute_many(reqs_get_users)
        for i in range(len(responses)):
            invitation = invitations[i]
            user = responses[i]
            invitation.get("metadata")["user"] = user
    elif postulant_uid is not None:
        params["postulant_uid"] = postulant_uid
        invitations = Services.get(url, resource, params)
        url = config.USER_SERVICE_URL
        resource = f"users/{postulant_uid}"
        params = {}
        user = Services.get(url, resource, params)
        for invitation in invitations:
            invitation.get("metadata")["user"] = user

    else:
        raise HTTPException(status_code=400, detail="Must send postulant_uid or tid")
    return invitations


@router.put("/invitations/teams/{tiid}", tags=["invitations"])
async def update_team_invitations(tiid: str, invitation: TeamInvitationUpdate):
    url = config.TEAM_SERVICE_URL
    resource = f"/team_invitations/{tiid}"
    params = {}
    result = Services.put(url, resource, params, invitation.json())
    if invitation.state == States.ACCEPTED:
        url = config.TEAM_SERVICE_URL
        resource = f"teams/{result.get('tid')}/members/{result.get('postulant_uid')}"
        params = {}
        Services.post(url, resource, params)

    return result

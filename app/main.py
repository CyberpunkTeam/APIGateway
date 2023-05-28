from fastapi import FastAPI, Security, Request, HTTPException

from .routers import (
    users,
    state,
    teams,
    profiles,
    notifications,
    projects,
    invitations,
    searches,
    authentication,
    recommendations,
    contents,
    home,
)
from fastapi.middleware.cors import CORSMiddleware

from .routers.authentication import authenticate
from .utils.authenticator import Authenticator
from .utils.blocker_manager import BlockerManager

app = FastAPI()
blocker_manager = BlockerManager()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    auth_token = request.headers.get("X-Tiger-Token")
    if auth_token is not None and "Bearer" in auth_token:
        token = auth_token.replace("Bearer ", "")
        if not (token in ("gonza", "mati")):
            token_decoded = Authenticator.decode_token(token)
            user_id = token_decoded.get("user_id")
            if blocker_manager.is_blocked_user(user_id):
                raise HTTPException(status_code=403, detail="User is blocked")
            if Authenticator.is_expired(token):
                new_token = Authenticator.create_token(user_id)
                response.headers["Token-Refresh"] = new_token

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router, dependencies=[Security(authenticate)])
app.include_router(users.router, dependencies=[Security(authenticate)])
app.include_router(state.router, dependencies=[Security(authenticate)])
app.include_router(teams.router, dependencies=[Security(authenticate)])
app.include_router(profiles.router, dependencies=[Security(authenticate)])
app.include_router(notifications.router, dependencies=[Security(authenticate)])
app.include_router(projects.router, dependencies=[Security(authenticate)])
app.include_router(invitations.router, dependencies=[Security(authenticate)])
app.include_router(searches.router, dependencies=[Security(authenticate)])
app.include_router(contents.router, dependencies=[Security(authenticate)])
app.include_router(home.router, dependencies=[Security(authenticate)])
app.include_router(authentication.router)

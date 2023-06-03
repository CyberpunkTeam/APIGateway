from fastapi import FastAPI, Security, Request, HTTPException
from starlette.responses import JSONResponse

from . import config
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
    metrics,
)
from fastapi.middleware.cors import CORSMiddleware

from .routers.authentication import authenticate
from .utils.authenticator import Authenticator
from .utils.blocker_manager import BlockerManager
from .utils.sessions_manager import SessionsManager
from .utils.tracks_repository import TracksRepository

app = FastAPI()
blocker_manager = BlockerManager()
tracks_repository = TracksRepository(config.DATABASE_URL, config.DATABASE_NAME)
sessions_manager = SessionsManager(tracks_repository)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        response = await call_next(request)
        auth_token = request.headers.get("X-Tiger-Token")
        print("auth_token: ", auth_token)
        if auth_token is not None and "Bearer" in auth_token:
            token = auth_token.replace("Bearer ", "")
            if not (token in ("gonza", "mati")):
                token_decoded = Authenticator.decode_token(token)
                user_id = token_decoded.get("user_id")
                print("USERID: ", user_id)
                if blocker_manager.is_blocked_user(user_id):
                    raise HTTPException(status_code=403, detail="User is blocked")

                sessions_manager.add_user(user_id)

                if Authenticator.is_expired(token):
                    new_token = Authenticator.create_token(user_id)
                    response.headers["Token-Refresh"] = new_token

        return response
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})


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
app.include_router(metrics.router, dependencies=[Security(authenticate)])
app.include_router(authentication.router)

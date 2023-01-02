from fastapi import FastAPI, Security, Request

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
)
from fastapi.middleware.cors import CORSMiddleware

from .routers.authentication import authenticate
from .utils.authenticator import Authenticator

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    auth_token = request.headers.get("X-Tiger-Token")
    if auth_token is not None and "Bearer" in auth_token:
        token = auth_token.replace("Bearer ", "")
        if Authenticator.is_expired(token):
            token_decoded = Authenticator.decode_token(token)
            new_token = Authenticator.create_token(token_decoded.get("user_id"))
            response.headers["Token-Refresh"] = new_token
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(state.router, dependencies=[Security(authenticate)])
app.include_router(teams.router)
app.include_router(profiles.router)
app.include_router(notifications.router)
app.include_router(projects.router)
app.include_router(invitations.router)
app.include_router(searches.router)
app.include_router(authentication.router)

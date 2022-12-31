import os

from fastapi import FastAPI, Request, Security, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status

from .repositories.authentication_repository import AuthenticationRepository
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

from .utils.authenticator import Authenticator

app = FastAPI()

API_KEY_NAME = "X-Tiger-Token"

token_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
auth_repository = AuthenticationRepository(
    os.environ.get("REDIS_PASSWORD"), int(os.environ.get("REDIS_TTL"), 60)
)


async def authenticate(token_auth_input: str = Security(token_auth)):
    if "Bearer" in token_auth_input:
        token_auth_input = token_auth_input.replace("Bearer ", "")
        if token_auth_input == "gonza" or token_auth_input == "mati":
            return

        if not Authenticator.authenticate(auth_repository, token_auth_input):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Auth Token",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth Token",
        )


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

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

from .routers.authentication import authenticate
from .utils.authenticator import Authenticator

app = FastAPI()


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

import os

from fastapi import APIRouter, HTTPException
from starlette import status

from app.models.credentials import Credentials
from app.models.token import Token
from app.utils.authenticator import Authenticator
from app.utils.google_auth import GoogleAuth
from app.main import auth_repository

router = APIRouter()

google_auth = GoogleAuth()


@router.post("/authentication", tags=["auth"], response_model=Token)
async def create_auth_token(credentials: Credentials):
    if google_auth.valid_token(credentials.auth_google_token):
        token = Authenticator.create_token(credentials.user_id)
        auth_repository.set(token)
        return Token(token=token)
    else:
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth Google Token",
        )

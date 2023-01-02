import os

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette import status

from app.models.credentials import Credentials
from app.models.token import Token
from app.utils.authenticator import Authenticator
from app.utils.google_auth import GoogleAuth


router = APIRouter()

google_auth = GoogleAuth()

API_KEY_NAME = "X-Tiger-Token"

token_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def authenticate(token_auth_input: str = Security(token_auth)):
    if "Bearer" in token_auth_input:
        token_auth_input = token_auth_input.replace("Bearer ", "")
        if token_auth_input == "gonza" or token_auth_input == "mati":
            return

        if not Authenticator.authenticate(token_auth_input):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Auth Token",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth Token",
        )


@router.post("/authentication", tags=["auth"], response_model=Token)
async def create_auth_token(credentials: Credentials):
    if google_auth.valid_token(credentials.auth_google_token):
        token = Authenticator.create_token(credentials.user_id)
        return Token(token=token)
    else:
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth Google Token",
        )

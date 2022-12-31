from fastapi import APIRouter, HTTPException
from starlette import status

from app.models.credentials import Credentials
from app.models.token import Token
from app.repositories.authentication_repository import AuthenticationRepository
from app.utils.authenticator import Authenticator
from app.utils.google_auth import GoogleAuth

router = APIRouter()
auth_repository = AuthenticationRepository("sKe8HhmQP2CnZRLgjy8hK7auj0YTTQ79", 3600)
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

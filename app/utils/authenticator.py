import os
from datetime import datetime, timedelta

from fastapi import HTTPException
import jwt
from jwt import DecodeError


class Authenticator:
    @staticmethod
    def authenticate(authentication_repository, token):
        if Authenticator.is_expired(token):
            token_decoded = Authenticator.decode_token(token)
            new_token = Authenticator.create_token(token_decoded.get("user_id"))
            if not authentication_repository.set(new_token):
                raise HTTPException(status_code=500, detail="Error to refresh token")
            else:
                return True

        valid_token = authentication_repository.get(token)
        if valid_token is None:
            return False
        else:
            return True

    @staticmethod
    def create_token(user_id):
        local = datetime.now()

        value = {
            "user_id": user_id,
            "created_date": local.strftime("%d-%m-%Y:%H:%M:%S"),
        }
        encoded_jwt = jwt.encode(
            value, os.environ.get("token", "secret"), algorithm="HS256"
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token):
        try:
            return jwt.decode(
                token, os.environ.get("token", "secret"), algorithms=["HS256"]
            )
        except DecodeError as e:
            raise HTTPException(status_code=400, detail="Invalid auth token")

    @staticmethod
    def is_expired(token):
        value = Authenticator.decode_token(token)
        created_date = datetime.strptime(value.get("created_date"), "%d-%m-%Y:%H:%M:%S")
        date = datetime.now()
        date -= timedelta(days=int(os.environ.get("TTL_DAYS", 1)))

        return created_date < date

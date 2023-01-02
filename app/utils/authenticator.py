import os
from datetime import datetime, timedelta

from fastapi import HTTPException
import jwt
from jwt import DecodeError


class Authenticator:
    @staticmethod
    def authenticate(token):
        try:
            Authenticator.decode_token(token)
            return True
        except:
            return False

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

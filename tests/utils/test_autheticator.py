import pytest
from fastapi import HTTPException

from app.utils.authenticator import Authenticator


def test_create_and_validate_token():
    user_id = "1"
    token = Authenticator.create_token(user_id)

    token_decoded = Authenticator.decode_token(token)

    assert token_decoded.get("user_id") == user_id

    assert Authenticator.is_expired(token) is False


def test_decode_invalid_token():
    with pytest.raises(HTTPException) as e_info:
        invalid_token = "adsdsasdas"
        Authenticator.decode_token(invalid_token)

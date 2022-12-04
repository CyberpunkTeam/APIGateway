import pytest
import requests_mock
from fastapi import HTTPException

from app.utils.rest_client import RestClient


def test_success_request():
    url = "http://test.com/"

    with requests_mock.Mocker() as m:
        json = {"challenges": []}
        m.register_uri("GET", url, json=json, status_code=200)

        json_response = RestClient.get(url)

        assert json_response == json


def test_status_500():
    with pytest.raises(HTTPException) as e_info:

        url = "http://test.com/"

        with requests_mock.Mocker() as m:
            json = {"message": "internal server error"}
            m.register_uri("GET", url, json=json, status_code=500)

            RestClient.get(url)


def test_status_400():
    with pytest.raises(HTTPException) as e_info:
        url = "http://test.com/"

        with requests_mock.Mocker() as m:
            json = {"message": "not found"}
            m.register_uri("GET", url, json=json, status_code=400)

            RestClient.get(url)

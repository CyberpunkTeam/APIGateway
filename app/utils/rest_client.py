from fastapi import HTTPException
from json import JSONDecodeError

import requests


class RestClient:
    @staticmethod
    def get(url):
        response = requests.get(url)
        return RestClient.handle_response(response)

    @staticmethod
    def post(url, json):
        response = requests.post(url, json=json)
        return RestClient.handle_response(response)

    @staticmethod
    def patch(url, json):
        response = requests.patch(url, json=json)
        return RestClient.handle_response(response)

    @staticmethod
    def handle_response(response):
        try:
            status = response.status_code

            if status >= 500:
                raise HTTPException(status_code=status, detail="internal server error")
            elif status >= 400:
                json = response.json()
                message = json.get("message", "Not Found")
                if "detail" in json:
                    message = json.get("detail")
                raise HTTPException(status_code=status, detail=message)
            else:
                json = response.json()

            return json
        except JSONDecodeError:
            raise HTTPException(status_code=500, detail="internal server error")

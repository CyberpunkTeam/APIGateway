from fastapi import HTTPException
from json import JSONDecodeError

import requests


class RestClient:
    @staticmethod
    def get(url, headers):
        if headers == {}:
            response = requests.get(url)
        else:
            response = requests.get(url, headers=headers)
        return RestClient.handle_response(response)

    @staticmethod
    def post(url, headers, json):
        if headers == {}:
            response = requests.post(url, json=json)
        else:
            response = requests.post(url, json=json, headers=headers)
        return RestClient.handle_response(response)

    @staticmethod
    def put(url, headers, json):
        if headers == {}:
            response = requests.put(url, json=json)
        else:
            response = requests.put(url, json=json, headers=headers)
        return RestClient.handle_response(response)

    @staticmethod
    def handle_response(response):
        try:
            status = response.status_code
            print(f"Status code: {status}")
            print(f"Text: {response.text}")
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

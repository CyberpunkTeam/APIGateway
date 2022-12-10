from fastapi import HTTPException
from json import JSONDecodeError

import requests


class RestClient:
    @staticmethod
    def get(url, headers):
        try:
            print("entra el get")
            if headers == {}:
                response = requests.get(url)
            else:
                response = requests.get(url, headers=headers)
            print("termina el get")
            return RestClient.handle_response(response)
        except Exception as e:
            print(f"Error: {e}")
            raise e

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
        print("entra al handle response")
        try:
            print(f"Status code: {response.content}")
            print(f"Text: {response.text}")
            status = response.status_code
            print(f"Status code: {status}")
            if status >= 500:
                raise HTTPException(status_code=status, detail="internal service error")
            elif status >= 400:
                message = response.text
                if "application/json" in response.headers.get("Content-Type", ""):
                    json = response.json()
                    message = json.get("message", "Not Found")
                    if "detail" in json:
                        message = json.get("detail")
                raise HTTPException(status_code=status, detail=message)
            else:
                if "application/json" in response.headers.get("Content-Type", ""):
                    json = response.json()
                else:
                    json = response.text

            return json
        except JSONDecodeError:
            raise HTTPException(status_code=500, detail="internal server error")

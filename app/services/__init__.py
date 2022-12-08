import os

from app.utils.http_parser import HttpParser
from app.utils.rest_client import RestClient
import google.auth.transport.requests
import google.oauth2.id_token


class Services:
    @staticmethod
    def get(url, resource, params={}, body=None):
        headers = {}
        if os.environ.get("MODE", "") != "DEV":
            headers = Services.get_authorized_headers_request(url)
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.get(endpoint, headers)

    @staticmethod
    def post(url, resource, params={}, body={}):
        headers = {}
        if os.environ.get("MODE", "") != "DEV":
            headers = Services.get_authorized_headers_request(url)
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.post(endpoint, headers, body)

    @staticmethod
    def put(url, resource, params={}, body={}):
        headers = {}
        if os.environ.get("MODE", "") != "DEV":
            headers = Services.get_authorized_headers_request(url)
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.put(endpoint, headers, body)

    @staticmethod
    def get_authorized_headers_request(audience):
        """
        make_authorized_get_request makes a GET request to the specified HTTP endpoint
        by authenticating with the ID token obtained from the google-auth client library
        using the specified audience value.
        """

        # Cloud Run uses your service's hostname as the `audience` value
        # audience = 'https://my-cloud-run-service.run.app/'
        # For Cloud Run, `endpoint` is the URL (hostname + path) receiving the request
        # endpoint = 'https://my-cloud-run-service.run.app/my/awesome/url'

        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
        print(f"Authorization Bearer {id_token}")
        return {"Authorization": f"Bearer {id_token}"}

import os

from app.utils.http_parser import HttpParser
from app.utils.rest_client import RestClient
import google.auth.transport.requests
import google.oauth2.id_token


class Services:
    @staticmethod
    def get(url, resource, params={}, body=None):
        headers = {}
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.get(endpoint, headers)

    @staticmethod
    def post(url, resource, params={}, body={}):
        headers = {}
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.post(endpoint, headers, body)

    @staticmethod
    def put(url, resource, params={}, body={}):
        headers = {}
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.put(endpoint, headers, body)

from app.utils.http_parser import HttpParser
from app.utils.rest_client import RestClient


class Services:
    @staticmethod
    def get(url, resource, params={}, body=None):
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.get(endpoint)

    @staticmethod
    def post(url, resource, params={}, body={}):
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.post(endpoint, body)

    @staticmethod
    def put(url, resource, params={}, body={}):
        endpoint = url + resource + HttpParser.parse_params(params)
        return RestClient.post(endpoint, body)

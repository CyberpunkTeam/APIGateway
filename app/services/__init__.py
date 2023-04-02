import asyncio
from functools import partial
from threading import Thread
import aiohttp

from app.utils.async_rest_client import AsyncRestClient
from app.utils.http_parser import HttpParser
from app.utils.rest_client import RestClient


class Services:
    @staticmethod
    def get(url, resource, params={}, body=None, async_mode=False):
        headers = {}
        endpoint = url + resource + HttpParser.parse_params(params)
        if async_mode:
            return partial(AsyncRestClient.get, endpoint)
        return RestClient.get(endpoint, headers)

    @staticmethod
    def post(url, resource, params={}, body={}, async_mode=False):
        headers = {}
        endpoint = url + resource + HttpParser.parse_params(params)
        if async_mode:
            return partial(AsyncRestClient.post, endpoint, body)
        return RestClient.post(endpoint, headers, body)

    @staticmethod
    def put(url, resource, params={}, body={}, async_mode=False):
        headers = {}
        endpoint = url + resource + HttpParser.parse_params(params)
        if async_mode:
            return partial(AsyncRestClient.put, endpoint, body)
        return RestClient.put(endpoint, headers, body)

    @staticmethod
    def _execute_many(requests_list, result):
        async def execute_concurrent(requests_to_create):
            async with aiohttp.ClientSession() as session:
                tasks = []
                for request in requests_to_create:
                    tasks.append(asyncio.ensure_future(request(session)))
                return await asyncio.gather(*tasks)

        result["result"] = asyncio.run(execute_concurrent(requests_list))

    @staticmethod
    def execute_many(
        requests_list,
    ):
        result = {}
        t = Thread(
            target=Services._execute_many,
            args=(
                requests_list,
                result,
            ),
        )
        t.start()
        t.join()

        return result["result"]

    @staticmethod
    def delete(url, resource, params, async_mode=False):
        headers = {}
        endpoint = url + resource + HttpParser.parse_params(params)
        if async_mode:
            return partial(AsyncRestClient.delete, endpoint)
        return RestClient.delete(endpoint, headers)

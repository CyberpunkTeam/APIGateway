from http.client import HTTPException


class AsyncRestClient:
    @staticmethod
    async def get(url, session):
        async with session.get(url) as resp:
            status = resp.status
            if 200 <= status < 400:
                return await resp.json()
            else:
                print(f"Error to get:{url} - status: {status}")
                return {}

    @staticmethod
    async def post(url, body, session):
        async with session.post(url, json=body) as resp:
            status = await resp.status
            if 200 <= status < 400:
                return await resp.json()
            elif 400 <= status < 500:
                if "application/json" in resp.headers.get("Content-Type", ""):
                    json = await resp.json()
                    message = json.get("message", "Not Found")
                    if "detail" in json:
                        message = json.get("detail")
                raise HTTPException(status_code=status, detail=message)
            else:
                print(f"Error to get:{url} - status: {status}")
                return None

    @staticmethod
    async def put(url, body, session):
        async with session.put(url, json=body) as resp:
            status = await resp.status
            if 200 <= status < 400:
                return await resp.json()
            elif 400 <= status < 500:
                if "application/json" in resp.headers.get("Content-Type", ""):
                    json = resp.json()
                    message = await json.get("message", "Not Found")
                    if "detail" in json:
                        message = json.get("detail")
                raise HTTPException(status_code=status, detail=message)
            else:
                print(f"Error to get:{url} - status: {status}")
                return None

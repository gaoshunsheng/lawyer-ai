import httpx

from app.core.config import settings


class UpstashRedis:
    """Upstash Redis REST API client."""

    def __init__(self):
        self._url = settings.UPSTASH_REDIS_REST_URL
        self._token = settings.UPSTASH_REDIS_REST_TOKEN

    async def get(self, key: str) -> str | None:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self._url}/get/{key}",
                headers={"Authorization": f"Bearer {self._token}"},
            )
            data = res.json()
            return data.get("result")

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        url = f"{self._url}/set/{key}/{value}"
        if ex:
            url += f"?EX={ex}"
        async with httpx.AsyncClient() as client:
            res = await client.get(
                url,
                headers={"Authorization": f"Bearer {self._token}"},
            )
            return res.json().get("result") == "OK"

    async def delete(self, *keys: str) -> int:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"{self._url}/del/{'/'.join(keys)}",
                headers={"Authorization": f"Bearer {self._token}"},
            )
            return res.json().get("result", 0)


redis = UpstashRedis()

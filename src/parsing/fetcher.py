import random

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

_TIMEOUT = httpx.Timeout(15.0)


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in {429, 500, 502, 503, 504}
    return isinstance(exc, (httpx.TimeoutException, httpx.ConnectError))


class ArticleFetcher:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )
    async def fetch(self, url: str) -> str:
        headers = {"User-Agent": random.choice(_USER_AGENTS)}
        response = await self._client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    async def close(self) -> None:
        await self._client.aclose()

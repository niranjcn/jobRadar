"""Retrying HTTP client for source adapters.

External boards are unreliable: single dropped connections (ConnectError,
ConnectTimeout, ReadTimeout, RemoteProtocolError, DNS failures) and transient
server errors (429/5xx) are common and expected. Every adapter goes through
this client so a transient failure is retried with exponential backoff instead
of failing the whole source. See AGENTS.md "Error Handling".
"""

import asyncio
import random

import httpx

MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 8.0

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _backoff(attempt: int) -> float:
    delay = min(BASE_BACKOFF_SECONDS * (2**attempt), MAX_BACKOFF_SECONDS)
    return delay + random.uniform(0, 0.5)


class RetryingClient(httpx.AsyncClient):
    """httpx.AsyncClient that retries transient failures with exponential backoff.

    Retries:
      - TransportError (connection refused/reset, DNS failures, connect/read
        timeouts, server disconnects mid-response)
      - HTTP 429, 500, 502, 503, 504

    Does NOT retry other 4xx responses (400/401/403/404/422...) - those are
    deterministic and retrying would only hammer the board.
    """

    async def request(self, method: str, url: str, *, retries: int = MAX_RETRIES, **kwargs) -> httpx.Response:
        last_response: httpx.Response | None = None
        for attempt in range(retries + 1):
            try:
                response = await super().request(method, url, **kwargs)
                if response.status_code not in RETRYABLE_STATUS_CODES or attempt >= retries:
                    return response
                last_response = response
            except httpx.TransportError:
                if attempt >= retries:
                    raise
            await asyncio.sleep(_backoff(attempt))
        assert last_response is not None
        return last_response
"""HTTP access to the local investments endpoint."""
from __future__ import annotations

import time

import requests
import json
from loguru import logger


class ApiClient:
    def __init__(self, url: str, timeout: int = 10) -> None:
        self._url = url
        self._timeout = timeout
        self._session = requests.Session()
        logger.debug("ApiClient configured | url={} timeout={}s", url, timeout)

    def fetch(self) -> dict:
        """GET the summary endpoint and return the decoded JSON dict.

            Raises ``requests.RequestException`` on failure.
        """
        logger.debug("GET {}", self._url)
        t0 = time.monotonic()
        resp = self._session.get(self._url, timeout=self._timeout)
        resp.raise_for_status()
        elapsed_ms = (time.monotonic() - t0) * 1000
        logger.debug("Response received in {:.0f}ms ({} bytes)", elapsed_ms, len(resp.content))
        return resp.json()
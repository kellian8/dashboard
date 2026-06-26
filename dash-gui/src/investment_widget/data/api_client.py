"""HTTP access to the local investments endpoint (stdlib only)."""
from __future__ import annotations

import json
import urllib.request


class ApiClient:
    def __init__(self, url: str, timeout: int = 10) -> None:
        self._url = url
        self._timeout = timeout

    def fetch(self) -> dict:
        """GET the summary endpoint and return the decoded JSON dict.

        Raises ``urllib.error.URLError`` / ``TimeoutError`` on failure.
        """
        with urllib.request.urlopen(self._url, timeout=self._timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

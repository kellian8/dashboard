from os import environ
from typing import Dict, List, Optional, Union

import requests
from loguru import logger
from requests.exceptions import RequestException

from ..config import BASE_URL, ENDPOINTS


class InvestmentsService:
    def get_summary(self) -> Optional[Dict]:
        # Build the full endpoint URL for the account summary
        url = f"{BASE_URL}{ENDPOINTS.summary}"
        _username = environ.get('TRADING212_KEY_ID')
        _password = environ.get('TRADING212_AUTH_KEY')

        # Guard against missing API key before making any network calls
        if _username is None or _password is None:
            raise RuntimeError(
                "investment API credentials are required. Please check they are loaded from environment correctly"
            )

        logger.debug("Credential check - usr/= {} pswd/= {}", _username, _password)
        try:
            logger.info(f"Fetching account summary from {url}")
            res = requests.get(
                url,
                headers={"Authorization": _username},
                auth=(_username, _password),
                timeout=5,
            )
            # TODO: FIX - task exists to scheduler with a success status whether the request is successful or not
            if res.ok:
                logger.success("Account summary data fetched successfully!")
                data: Dict = res.json()
                return data
            else:
                logger.warning(f"Request returned non-OK status: {res.reason} - {res.text}")

        except RequestException as e:
            logger.error("An error occurred while fetching trading account summary")
            raise e

        return None

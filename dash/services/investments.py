from os import environ

import requests
from loguru import logger
from requests.exceptions import RequestException

from ..config import _ENDPOINTS, BASE_URL


class InvestmentsService:
    def getSummary(self):
        # Build the full endpoint URL for the account summary
        url = f"{BASE_URL}{_ENDPOINTS.summary}"
        _username = environ.get('TRADING212_KEY_ID')

        # Guard against missing API key before making any network calls
        if _username is None:
            logger.error("TRADING212_KEY_ID environment variable is not set — cannot fetch account summary")
            return

        logger.info(f"Fetching account summary from {url}")

        try:
            res = requests.get(
                url,
                headers={"Authorization": _username},
                auth=(_username, environ.get('TRADING212_AUTH_KEY')),
                timeout=5,
            )

            logger.debug(f"Response status: {res.status_code}")

            if res.ok:
                data = res.json()
                logger.debug(f"Raw response data: {data}")

                # Extract the nested investments object; default to empty dict if missing
                investments = data.get("investments", {})

                # Flatten the relevant properties into a list of key/value dicts.
                # Excludes: cash, id, currency
                result = [
                    {"key": "currentValue", "value": investments.get("currentValue")},
                    {"key": "realizedProfitLoss", "value": investments.get("realizedProfitLoss")},
                    {"key": "totalCost", "value": investments.get("totalCost")},
                    {"key": "unrealizedProfitLoss", "value": investments.get("unrealizedProfitLoss")},
                    # totalValue lives at the top level of the response
                    {"key": "totalValue", "value": data.get("totalValue")},
                ]

                logger.debug(f"Parsed summary result: {result}")
            else:
                logger.warning(f"Request returned non-OK status: {res.status_code} - {res.text}")

        except RequestException as e:
            logger.error("An error occurred while fetching trading account summary")
            logger.error(e)
        else:
            logger.success("Account summary data fetched successfully!")

from os import environ

from pydantic import BaseModel

BASE_URL = environ.get('TRADING212_API_BASE_URL')


class _Endpoints(BaseModel):
    model_config = {"frozen": True}

    summary: str = "/equity/account/summary"


_ENDPOINTS = _Endpoints()

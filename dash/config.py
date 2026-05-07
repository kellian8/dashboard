from datetime import time
from os import environ
from typing import List

from pydantic import BaseModel

BASE_URL = environ.get('TRADING212_API_BASE_URL')


class Endpoints(BaseModel):
    model_config = {"frozen": True}

    summary: str = "/equity/account/summary"


class FetchSummaryTaskConfig(BaseModel):
    model_config = {"frozen": True}

    name: str = "fetch_investment_summary"
    scheduled_times: List[time] = [
        time(hour=0, minute=3, second=0),
        # time(hour=8, minute=10, second=40),
    ]


ENDPOINTS = Endpoints()

TaskConfigs = {"FETCH_SUMMARY": FetchSummaryTaskConfig()}

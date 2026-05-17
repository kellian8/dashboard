from datetime import time
from os import environ, path
from typing import List

from pydantic import BaseModel


class Endpoints(BaseModel):
    model_config = {"frozen": True}

    summary: str = "/equity/account/summary"


class Files(BaseModel):
    model_config = {"frozen": True}

    source_root_dir: str = path.dirname(__file__)
    temp_dir: str = path.join(path.abspath(path.dirname(__file__)), "temp")


# TASK CONFIGURATIONS
class FetchSummaryTaskConfig(BaseModel):
    model_config = {"frozen": True}

    name: str = "fetch_investment_summary"
    scheduled_times: List[time] = [
        time(hour=22, minute=20, second=50),
        # time(hour=8, minute=10, second=40),
    ]


TaskConfigs = {"FETCH_SUMMARY": FetchSummaryTaskConfig()}


FILES = Files()

BASE_URL = environ.get('TRADING212_BASE_URL')

ENDPOINTS = Endpoints()

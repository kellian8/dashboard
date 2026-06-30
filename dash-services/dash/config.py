from datetime import datetime, time, timedelta
from os import path, getenv
import os
from types import SimpleNamespace
from typing import Any, Dict, Optional

from pydantic import BaseModel, model_validator


class Endpoints(BaseModel):
    model_config = {"frozen": True}

    summary: str = "/equity/account/summary"
    push_summary: str = "/ingest/summary"


class _FrozenNamespace(SimpleNamespace):
    """Read-only SimpleNamespace. Raises AttributeError on mutation."""

    def __setattr__(self, name, value):
        raise AttributeError("Config namespace is read-only")

    def __delattr__(self, name):
        raise AttributeError("Config namespace is read-only")


# TASK CONFIGURATIONS
TaskConfigs = {
    "FETCH_SUMMARY": _FrozenNamespace(
        name="fetch_investment_summary",
        schedules=[
            _FrozenNamespace(type="recurring_time", time=time(hour=7, minute=30, second=0)),
            _FrozenNamespace(type="recurring_time", time=time(hour=8, minute=30, second=0)),
            _FrozenNamespace(type="recurring_time", time=time(hour=4, minute=30, second=0)),
            _FrozenNamespace(type="recurring_time", time=time(hour=14, minute=0, second=0)),
            _FrozenNamespace(type="recurring_time", time=time(hour=21, minute=30, second=0)),
        ],
        callback="update_gui_summary",
    ),
    "UPDATE_GUI_SUMMARY": _FrozenNamespace(
        name="update_gui_summary",
        schedules=[],
        callback=None,
    ),
}

## __________________________________ CONSTANTS _____________________________________

ROOT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
T212_BASE_URL = getenv('TRADING212_BASE_URL')

# GUI configuration
GUI_HOST = getenv('GUI_HOST')
GUI_PORT = getenv('GUI_PORT')

# Server configuration
SERVER_HOST = getenv('SERVER_HOST')
SERVICES_DEFAULT_PORT = 8000
SERVICES_PORT = int(getenv('SERVICES_PORT', SERVICES_DEFAULT_PORT))

# in seconds. Delay before executing a callback task after the main task completes.
CALLBACK_DELAY = 15

ENDPOINTS = Endpoints()

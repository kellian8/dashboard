from datetime import datetime, time, timedelta
from os import environ, path
from types import SimpleNamespace
from typing import Any, Dict, Optional

from pydantic import BaseModel, model_validator


class _FrozenNamespace(SimpleNamespace):
    """Read-only SimpleNamespace. Raises AttributeError on mutation."""

    def __setattr__(self, name, value):
        raise AttributeError("Config namespace is read-only")

    def __delattr__(self, name):
        raise AttributeError("Config namespace is read-only")


class _TaskConfigSchedule(BaseModel):
    """Read-only SimpleNamespace. Raises AttributeError on mutation."""

    # type of schedule being created. Must requires corresonding ScheduleStrategy
    type: str
    # Time of day - for RecurringTimeSchedulingStrategy
    time: Optional[time] = None
    # Interval between executions - for RecurringSchedulingStrategy
    interval: Optional[timedelta] = None
    # Single execution - for OneTimeSchedulingStrategy
    execution_time: Optional[datetime] = None

    @model_validator(mode='before')
    def execution_time_initialiser_required(cls, params: Any):
        # Ensure config schedule contains a vaild execution time initialiser.
        if isinstance(params, Dict):
            for ex_time in ('time', 'interval', 'execution_time'):
                if params.get(ex_time) is not None:
                    return params
            raise ValueError("You must provide a time initialiser to TaskCondigSchedule")
        else:
            raise TypeError("Unable to check params. Not provided to validator as Dict")


class Endpoints(BaseModel):
    model_config = {"frozen": True}

    summary: str = "/equity/account/summary"


class Files(BaseModel):
    model_config = {"frozen": True}

    source_root_dir: str = path.dirname(__file__)
    temp_dir: str = path.join(path.abspath(path.dirname(__file__)), "temp")


# TASK CONFIGURATIONS
TaskConfigs = {
    "FETCH_SUMMARY": _FrozenNamespace(
        name="fetch_investment_summary",
        schedules=[
            # _FrozenNamespace(type="recurring_time", time=time(hour=22, minute=2, second=30)),
            # _FrozenNamespace(type="recurring_time", time=time(hour=8, minute=10, second=40)),
            _TaskConfigSchedule(type="interval", interval=timedelta(seconds=30)),
            # _FrozenNamespace(type="one_time", execution_time=datetime(2026, 6, 1, 22, 0)),
        ],
    )
}


FILES = Files()

BASE_URL = environ.get('TRADING212_BASE_URL')

ENDPOINTS = Endpoints()

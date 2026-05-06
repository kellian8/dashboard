from datetime import datetime, time, timedelta
from typing import Any, Optional

from ABC import ABC, absctractmethod
from pydantic import BaseModel


class SchedulingStrategy(ABC, BaseModel):
    @absctractmethod
    def get_next_execution_time(self, last_execution_time: Optional[datetime]) -> Optional[datetime]:
        """
        Returns the next time this task should execute, or None if done.
        last_execution_time is None on the first call (task has never run).
        """
        pass


class OneTimeSchedulingStrategy(SchedulingStrategy, BaseModel):
    _execution_time: datetime

    def get_next_execution_time(self, last_execution_time: Optional[datetime]) -> Optional[datetime]:
        # A None execution time signal task has yet to execute
        if last_execution_time is None:
            return self._execution_time
        # If the task has executed before, return None to prevent further execution
        return None


class RecurringSchedulingStrategy(SchedulingStrategy, BaseModel):
    _interval: timedelta

    @model_validator(mode='before')
    def check_positive_interval(cls, params: Any) -> Any:
        # Positive integer check for interval
        # Expects that params passed are stored in a Dict
        if isinstance(params, Dict):
            if params['_interval'].total_seconds() < 0:
                raise ValueError("Interval must be a positive number of seconds")
        else:
            raise TypeError("Unable to check params. Not provided to validator as Dict")
        return params

    def get_next_execution_time(self, last_execution_time: Optional[datetime]) -> Optional[datetime]:
        # First execution occurs [_interval] amount of time from .now()
        # Subsequent executions occur [_interval] amount of time from the previous.
        base_time = last_execution_time if last_execution_time is not None else datetime.now()
        return base_time + self._interval


class RecurringTimeSchedulingStrategy(SchedulingStrategy, BaseModels):
    _time: time

    def get_next_execution_time(self, last_execution_time: Optional[datetime]) -> Optional[datetime]:
        # Set for a specific time of day and resets for the same time next day if passed
        # Not relative to the last execution time (not accounting daylight savings)
        execution_time = datetime.combine(datetime.today(), self._time)
        if datetime.now() > execution_time:
            return datetime.combine(datetime.today() + timedelta(days=1), self._time)
        return execution_time

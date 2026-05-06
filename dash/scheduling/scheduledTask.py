import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator


class ScheduledTask(BaseModel):
    _id: str = str(uuid.uuid4())
    _task: Task
    _strategy: SchedulingStrategy
    _sequenceNumber: int
    _last_execution_time: datetime = None
    _status: TaskStatus = TaskStatus.SCHEDULED

    @model_validator(mode='after')
    def set_next_executed_time(self):
        # Ask the strategy for the initial execution time.
        # Passing None signals "this task has never run before."
        self._next_execution_time: Optional[datetime] = strategy.get_next_execution_time(None)
        return self

    @property
    def id(self) -> str:
        return self._id

    @property
    def task(self) -> Task:
        return self._task

    @property
    def next_execution_time(self) -> Optional[datetime]:
        return self._next_execution_time

    @property
    def status(self) -> TaskStatus:
        return self._status

    @status.setter
    def status(self, value: TaskStatus) -> None:
        self._status = value

    def has_more_executions(self):
        return self.strategy.get_next_executed_time(self._last_execution_time) is not None

    # Called after execution completes. Records the actual finish time
    # then asks the strategy for the next run.
    def update_for_next_execution():
        self._last_execution_time = datetime.now()
        next_time = self._strategy.get_next_executed_time(self._last_execution_time)
        self._next_execution_time = next_time

    def __lt__(self, other: 'ScheduledTask') -> bool:
        # None execution times get pushed to the back of the queue
        if self._next_execution_time is None and other._next_execution_time is None:
            return False
        if self._next_execution_time is None:
            return False
        if other._next_execution_time is None:
            return True

        # Primary sort: earliest execution time first (min-heap)
        if self._next_execution_time != other._next_execution_time:
            return self._next_execution_time < other._next_execution_time

        # Tiebreaker: lower sequence number first (FIFO for same-time tasks)
        return self._sequence_number < other._sequence_number

    def __repr__(self) -> str:
        return f"ScheduledTask[{self._task.get_name()}, next={self._next_execution_time}, status={self._status}]"

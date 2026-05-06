from enum import Enum

from pydantic import BaseModel


class TaskStatus(Enum, BaseModel):
    SCHEDULED: str = 'SCHEDULED'
    RUNNING: str = 'RUNNING'
    COMPLETED: str = 'COMPLETED'
    FAILED: str = 'FAILED'
    CANCELLED: str = 'CANCELLED'
